"""Managed validation copies remain standalone and refuse local drift."""

from collections.abc import Iterator
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest

from scripts.sync_validation_tools import FILES, RECORD, check_validation_tools, sync_validation_tools


@contextmanager
def repositories() -> Iterator[tuple[Path, Path]]:
    with tempfile.TemporaryDirectory() as temporary:
        source, target = Path(temporary) / 'uni', Path(temporary) / 'unif'
        for root, name in ((source, 'uni-skills'), (target, 'unif-portal-dev-skills')):
            root.mkdir()
            _ = (root / 'plugin.json').write_text(json.dumps({'name': name}))
        for relative in FILES:
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text('source: ' + relative)
        yield source, target


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}


class ValidationToolsTests(unittest.TestCase):
    def test_initial_adoption_check_and_explicit_upgrade(self) -> None:
        with repositories() as (source, target):
            sync_validation_tools(source, target)
            self.assertIsNone(check_validation_tools(source))
            self.assertIsNotNone(check_validation_tools(target))
            before = snapshot(target)
            sync_validation_tools(source, target, check=True)
            self.assertEqual(snapshot(target), before)
            _ = (source / FILES[0]).write_text('upgrade')
            with self.assertRaises(ValueError):
                sync_validation_tools(source, target, check=True)
            self.assertEqual(snapshot(target), before)
            sync_validation_tools(source, target)
            self.assertEqual((target / FILES[0]).read_text(), 'upgrade')

    def test_verification_does_not_require_the_source_checkout(self) -> None:
        with repositories() as (source, target):
            sync_validation_tools(source, target)
            _ = source.rename(source.with_name('source-unavailable'))
            _ = check_validation_tools(target)

    def test_modified_adopted_file_is_not_overwritten(self) -> None:
        with repositories() as (source, target):
            sync_validation_tools(source, target)
            _ = (target / FILES[0]).write_text('local change')
            before = snapshot(target)
            with self.assertRaises(ValueError):
                sync_validation_tools(source, target)
            self.assertEqual(snapshot(target), before)

    def test_missing_source_does_not_partially_update_the_target(self) -> None:
        with repositories() as (source, target):
            sync_validation_tools(source, target)
            before = snapshot(target)
            (source / FILES[-1]).unlink()
            with self.assertRaises(OSError):
                sync_validation_tools(source, target)
            self.assertEqual(snapshot(target), before)

    def test_unmanaged_existing_file_and_symlink_are_rejected(self) -> None:
        with repositories() as (source, target):
            path = target / FILES[0]
            path.parent.mkdir(parents=True)
            _ = path.write_text('unmanaged')
            with self.assertRaises(ValueError):
                sync_validation_tools(source, target)
            self.assertEqual(path.read_text(), 'unmanaged')
            path.unlink()
            path.symlink_to(source / FILES[0])
            with self.assertRaises(ValueError):
                sync_validation_tools(source, target)

    def test_missing_or_forged_record_is_rejected(self) -> None:
        with repositories() as (source, target):
            with self.assertRaises(OSError):
                _ = check_validation_tools(target)
            sync_validation_tools(source, target)
            _ = (target / RECORD).write_text(json.dumps({
                'formatVersion': 1, 'source': 'unrelated', 'files': {},
            }))
            with self.assertRaises(ValueError):
                _ = check_validation_tools(target)

    def test_wrong_source_is_rejected(self) -> None:
        with repositories() as (source, target):
            _ = (source / 'plugin.json').write_text('{"name":"unrelated"}')
            with self.assertRaises(ValueError):
                sync_validation_tools(source, target)

    def test_current_repository_adoption_is_consistent(self) -> None:
        _ = check_validation_tools(Path(__file__).resolve().parents[1])


if __name__ == '__main__':
    _ = unittest.main()
