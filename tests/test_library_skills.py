import shutil
import tempfile
import unittest
from pathlib import Path

import yaml
from skills_ref import validate as validate_skill

from scripts.validate_repository import check_markdown


LIBRARIES = {
    'unif-design': '@unif/react-native-design',
    'unif-chat': '@unif/react-native-chat',
    'unif-camera': '@unif/react-native-camera',
    'unif-hms-scan': '@unif/react-native-hms-scan',
    'unif-umeng': '@unif/react-native-umeng',
    'unif-icons': '@unif/react-native-icons',
}


class LibrarySkillDistributionTests(unittest.TestCase):
    def test_each_library_skill_can_be_distributed_without_sibling_files(self):
        source = Path(__file__).resolve().parents[1] / 'skills'
        for name, package in LIBRARIES.items():
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as temporary:
                self.assertTrue((source / name).is_dir(), f'Missing library entry: {name}')
                isolated = Path(temporary) / name
                shutil.copytree(source / name, isolated)
                self.assertEqual(validate_skill(isolated), [])
                frontmatter = yaml.safe_load(
                    (isolated / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
                )
                self.assertEqual(frontmatter['metadata']['package'], package)
                for document in isolated.rglob('*.md'):
                    check_markdown(isolated, document)


if __name__ == '__main__':
    unittest.main()
