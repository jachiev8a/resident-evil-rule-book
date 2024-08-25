import os
import re
from _python.settings import get_main_project_dir, get_config_data

MAIN_PROJECT_DIR = get_main_project_dir()
MAIN_CONFIG_DATA = get_config_data()


TEMPLATE_HORIZONTAL_LINE = "---\n\n"
TEMPLATE_GO_BACK = "### [<- ATRAS](../README.md)"

REGEX_README_RESOURCE = re.compile(r'{(\w*):([\w.]*)}')


class ConfigNode:

    MAIN_PROJECT_PATH = MAIN_PROJECT_DIR

    def __init__(
        self,
        node_name: str,
        config_data: dict,
        parent_node_dir: str = None,
        index: int = 0
    ):
        self._node_config = config_data
        self.index = index
        self.node_name = node_name
        self.node_title = self._get_node_title()
        self.go_back = config_data.get("go_back")
        self.readme = config_data.get("readme", None)
        self.node_dir_path = f"{self.MAIN_PROJECT_PATH}/{self.index}0_{self.node_name}"
        self.relative_path = self.node_dir_path.replace(f"{self.MAIN_PROJECT_PATH}/", '')
        self.parent_node_dir = parent_node_dir
        self.contents = config_data.get("contents", {})
        self.table_of_contents = []

        if self.parent_node_dir:
            self.node_dir_path = f"{self.parent_node_dir}/{self.index}0_{self.node_name}"
            self.relative_path = self.node_dir_path.replace(f"{self.parent_node_dir}/", '')

        # parse readme content looking for special keywords
        self._parse_readme_content()

    def _get_node_title(self):
        node_title = self._node_config.get("title")
        if not node_title:
            node_title = (self.node_name[0].upper() + self.node_name[1:]).replace('_', ' ')
        return node_title

    def _get_img_resource_path(self, img_resource_name: str):
        return (
            f"![alt {img_resource_name}]"
            "(https://github.com/jachiev8a/resident-evil-rule-book/blob/"
            f"master/_python/img/{img_resource_name}?raw=true)"
        )

    def _parse_readme_content(self):
        if not self.readme:
            self.readme = ""
            return

        all_matches = re.findall(REGEX_README_RESOURCE, self.readme)

        for _ in all_matches:
            # iterate over all matches and replace them with resource path
            match = re.search(REGEX_README_RESOURCE, self.readme)
            if match:
                resource_type = match.group(1)
                resource_name = match.group(2)
            else:
                # no more matches were found. Break infinite loop
                break

            if resource_type == 'img':
                img_resource_path = self._get_img_resource_path(resource_name)
                # replace first occurrence of resource with img resource path
                # TODO: this may need a refactor since we always think first occurrence is always in order
                self.readme = re.sub(REGEX_README_RESOURCE, img_resource_path, self.readme, count=1)
        # replace '\\n' with new line
        self.readme = self.readme.replace('\\n', '\n')

    def _get_go_back_template(self):
        return (
            f"\n"
            f"{TEMPLATE_HORIZONTAL_LINE}{TEMPLATE_GO_BACK}\n\n{TEMPLATE_HORIZONTAL_LINE}"
            f"\n"
        )

    def generate_readme(self):
        with open(f"{self.node_dir_path}/README.md", "w") as f:
            if self.go_back:
                f.write(self._get_go_back_template())
            f.write(f"\n### {self.node_title}\n\n")
            f.write(f"{self.readme}\n\n")

    def generate_title(self):
        if self.node_title:
            self.readme = self.readme + f"### {self.node_title}\n\n"

    def generate_table_of_contents(self):
        if self.table_of_contents:
            self.readme = self.readme + '\n'
            self.readme = self.readme + ''.join(self.table_of_contents)

    def generate(self):
        os.makedirs(self.node_dir_path, exist_ok=True)
        # if node has contents, generate child nodes for it (recursively)
        if self.contents:
            print(f"> Generating Config Parent Node [{self.node_name}] directory...")
            for index, (child_node_name, child_node_data) in enumerate(self.contents.items()):
                config_node = ConfigNode(
                    node_name=child_node_name,
                    config_data=child_node_data,
                    parent_node_dir=self.node_dir_path,
                    index=index,
                )
                config_node.generate()
                self.table_of_contents.append(
                    f"- ### [{config_node.node_title.upper()}]"
                    f"({config_node.relative_path}/README.md)\n"
                )
        else:
            print(f">>> Generating Config Child Node [{self.node_name}] directory...")
        self.generate_table_of_contents()
        self.generate_readme()


class ConfigGenerator:
    def __init__(self, configuration: dict):
        self.add_index_numbers = configuration.get("add_index_numbers")
        self.main_title = configuration.get("main_title")
        self.structure = configuration.get("structure")
        self.table_of_contents = []

    def generate_table_of_contents(self):
        with open(f"{MAIN_PROJECT_DIR}/README.md", "w") as f:
            f.write(f"# {self.main_title}\n\n")
            f.write(f"{TEMPLATE_HORIZONTAL_LINE}")
            f.write("".join(self.table_of_contents))

    def generate(self):
        for index, (node_name, configuration) in enumerate(self.structure.items()):
            config_node = ConfigNode(
                node_name=node_name,
                config_data=configuration,
                index=index,
            )
            self.table_of_contents.append(
                f"- ### [{config_node.node_title.upper()}]"
                f"({config_node.relative_path}/README.md)\n"
            )
            config_node.generate()
        self.generate_table_of_contents()


def main():
    config_generator = ConfigGenerator(configuration=MAIN_CONFIG_DATA)
    config_generator.generate()


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    main()
