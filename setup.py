from setuptools import setup


requires = []
with open('requirements.txt') as fid:
    for line in fid:
        line = line.strip()
        line = line.split('==')[0]
        line = line.split('@')[0]
        requires.append(line.strip())

setup( 
    name = 'AIdel視障助手', 
    version = '1.0', 
    description = 'AIdel視障助手的穿戴式裝置專案', 
    url = 'https://github.com/zhiao777774/AIdel', 
    author = '許智豪', 
    author_email = 'zhiaohsu@gmail.com',
    zip_safe = False, 
    include_package_data = True,
    install_requires = requires
)