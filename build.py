#!/usr/bin/env python3
import os
import shutil
from urllib.request import urlopen, urlretrieve
from xml.etree import ElementTree

root_dir = 'javadocs'

rxbinding = [{
    'name': 'RxBinding',
    'id': 'rxbinding',
}, {
    'name': 'RxBinding AppCompat v7',
    'id': 'rxbinding-appcompat-v7',
}, {
    'name': 'RxBinding Design',
    'id': 'rxbinding-design',
}, {
    'name': 'RxBinding LeanBack v17',
    'id': 'rxbinding-leanback-v17',
}, {
    'name': 'RxBinding RecyclerView v7',
    'id': 'rxbinding-recyclerview-v7',
}, {
    'name': 'RxBinding Support v4',
    'id': 'rxbinding-support-v4',
}]

readme_md_template = """
# {} Docset

## Author
 
Jaewe Heo ([@importre](https://github.com/importre))

## How to generate

### Prerequisites

- macOS
- python3

### Build

```sh
$ git clone https://github.com/importre/dash-docset-rxbinding
$ cd dash-docset-rxbinding
$ ./build.py  # see outputs directory
```

[RxBinding]: https://github.com/JakeWharton/RxBinding
"""

docset_json_template = """
{{
    "name": "{}",
    "version": "{}",
    "archive": "{}.tgz",
    "author": {{
        "name": "Jaewe Heo",
        "link": "https://github.com/importre"
    }},
    "aliases": ["rxbinding"],
    "specific_versions": [
        {{ 
            "version": "{}",
            "archive": "versions/{}/{}.tgz",
        }}
    ]
}}
"""


def download(url):
    meta_url = "{}/maven-metadata.xml".format(url)
    xml = urlopen(meta_url).read()
    root = ElementTree.fromstring(xml)
    latest_version = root.findall("./versioning/latest")[0].text
    artifact_id = root.findall("./artifactId")[0].text
    filename = "{}-{}-javadoc.jar".format(artifact_id, latest_version)
    javadoc_url = "{}/{}/{}".format(url, latest_version, filename)
    javadoc_file = os.sep.join([root_dir, filename])

    print(javadoc_file)
    urlretrieve(javadoc_url, javadoc_file)
    return javadoc_file, latest_version


def download_all():
    base = 'https://repo.maven.apache.org/maven2/com/jakewharton/rxbinding2'
    shutil.rmtree(root_dir, ignore_errors=True)
    os.makedirs(root_dir, exist_ok=True)

    for item in rxbinding:
        url = '{}/{}'.format(base, item['id'])
        filename, version = download(url)
        item['filename'] = filename
        item['version'] = version
    pass


def extract_jar_files():
    for item in rxbinding:
        filename = item['filename']
        dir_name = '{}/{}'.format(root_dir, item['id'])
        shutil.unpack_archive(filename, dir_name, 'zip')
    pass


def make_docset_files():
    os.system("rm -rf *.docset")
    for item in rxbinding:
        name = item['name']
        doc_dir = '{}/{}'.format(root_dir, item['id'])
        os.system('./javadocset "{}" "{}"'.format(name, doc_dir))
    pass


def make_outputs():
    cmd = 'tar --exclude=".DS_Store" -cvzf "{}.tgz" "{}.docset"'
    outputs_dir = 'outputs'
    shutil.rmtree(outputs_dir, ignore_errors=True)
    os.makedirs(outputs_dir, exist_ok=True)
    for item in rxbinding:
        artifact_id = item['id']
        version = item['version']
        name = item['name']

        tgz_name = artifact_id.replace("-", "_")
        id_dir = '{}/{}'.format(outputs_dir, tgz_name)
        version_dir = '{}/versions/{}'.format(id_dir, version)
        os.makedirs(version_dir)
        os.system(cmd.format('{}/{}'.format(id_dir, tgz_name), name))
        os.system(cmd.format('{}/{}'.format(version_dir, tgz_name), name))
        filename = '{}/README.md'.format(id_dir)
        with open(filename, 'w') as fout:
            readme_md = readme_md_template.format(
                name.replace('RxBinding', '[RxBinding]')
            ).strip()
            fout.write(readme_md)
        filename = '{}/docset.json'.format(id_dir)
        with open(filename, 'w') as fout:
            docset_json = docset_json_template.strip().format(
                name, version, artifact_id,
                version, version, artifact_id
            ).strip()
            fout.write(docset_json)
    os.system('open {}'.format(outputs_dir))
    pass


if __name__ == '__main__':
    download_all()
    extract_jar_files()
    make_docset_files()
    make_outputs()
    pass
