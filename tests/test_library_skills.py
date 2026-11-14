import shutil
import tempfile
import unittest
from pathlib import Path
from typing import TypedDict, cast

import yaml
from scripts.validate_repository import check_skills


LIBRARIES = {
    'unif-design': '@unif/react-native-design',
    'unif-chat': '@unif/react-native-chat',
    'unif-camera': '@unif/react-native-camera',
    'unif-hms-scan': '@unif/react-native-hms-scan',
    'unif-umeng': '@unif/react-native-umeng',
    'unif-icons': '@unif/react-native-icons',
    'unif-amap': '@unif/react-native-amap',
    'unif-files': '@unif/react-native-files',
    'unif-logger': '@unif/react-native-logger',
    'unif-oss': '@unif/react-native-oss',
    'unif-speech': '@unif/react-native-speech',
}
HARMONY_LIBRARIES = {
    f'unif-{name}': f'@unif/harmony-{name}'
    for name in ('icons', 'design', 'chat', 'camera', 'hms-scan', 'umeng', 'logger')
}


class LibraryMetadata(TypedDict):
    package: str
    harmony_package: str


class LibraryFrontmatter(TypedDict):
    metadata: LibraryMetadata


class LibrarySkillDistributionTests(unittest.TestCase):
    def test_each_library_preserves_metadata_and_references_when_installed_alone(self) -> None:
        source = Path(__file__).resolve().parents[1] / 'plugins'
        for name, package in LIBRARIES.items():
            with self.subTest(plugin=name), tempfile.TemporaryDirectory() as temporary:
                plugin = Path(temporary) / name
                _ = shutil.copytree(source / name, plugin, symlinks=True)
                self.assertEqual(check_skills(plugin, standalone=False), 1)
                isolated = plugin / 'skills' / name
                frontmatter = cast(LibraryFrontmatter, yaml.safe_load(
                    (isolated / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
                ))
                self.assertEqual(frontmatter['metadata']['package'], package)
                if name in HARMONY_LIBRARIES:
                    self.assertEqual(frontmatter['metadata']['harmony_package'], HARMONY_LIBRARIES[name])
                    self.assertTrue((isolated / 'references/harmony.md').is_file())


if __name__ == '__main__':
    _ = unittest.main()
