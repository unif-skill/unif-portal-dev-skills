import shutil
import tempfile
import unittest
from pathlib import Path

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


class LibrarySkillDistributionTests(unittest.TestCase):
    def test_each_library_skill_can_be_distributed_without_sibling_files(self):
        source = Path(__file__).resolve().parents[1] / 'skills'
        for name, package in LIBRARIES.items():
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as temporary:
                self.assertTrue((source / name).is_dir(), f'Missing library entry: {name}')
                isolated = Path(temporary) / 'skills' / name
                shutil.copytree(source / name, isolated, symlinks=True)
                self.assertEqual(check_skills(Path(temporary)), 1)
                frontmatter = yaml.safe_load(
                    (isolated / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
                )
                self.assertEqual(frontmatter['metadata']['package'], package)
                if name in HARMONY_LIBRARIES:
                    self.assertEqual(frontmatter['metadata']['harmony_package'], HARMONY_LIBRARIES[name])
                    self.assertTrue((isolated / 'references/harmony.md').is_file())


if __name__ == '__main__':
    unittest.main()
