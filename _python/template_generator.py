import os
import re
from _python.settings import get_main_project_dir, get_config_data

MAIN_PROJECT_DIR = get_main_project_dir()
MAIN_CONFIG_DATA = get_config_data()


TEMPLATE_HORIZONTAL_LINE = "---\n\n"
TEMPLATE_GO_BACK = "### [<- ATRAS](../README.md)"

REGEX_README_RESOURCE = re.compile(r'{(\w*):([\w.]*)}')


class ConfigNodeBaseClass:

    MAIN_PROJECT_PATH = MAIN_PROJECT_DIR

    def __init__(self, node_name: str, config_data: dict, index: int = 0):
        self.index = index
        self.node_name = node_name
        self.go_back = config_data.get("go_back")
        self.is_final_dir = config_data.get("is_final_dir")
        self.readme = config_data.get("readme", None)
        self.directory_path = f"{self.MAIN_PROJECT_PATH}/{self.index}0_{self.node_name}"
        self.contents = {}
        self._parse_readme_content()

    def _get_img_resource_path(self, img_resource_name: str):
        return (
            "![alt text]"
            "(https://github.com/jachiev8a/resident-evil-rule-book/blob/"
            f"master/_python/img/{img_resource_name}?raw=true)"
        )

    def _parse_readme_content(self):
        if not self.readme:
            self.readme = "EMPTY!"
            return

        resource_type = None
        resource_name = None
        match = re.search(REGEX_README_RESOURCE, self.readme)
        if match:
            resource_type = match.group(1)
            resource_name = match.group(2)

        if resource_type == 'img':
            img_resource_path = self._get_img_resource_path(resource_name)
            self.readme = re.sub(REGEX_README_RESOURCE, img_resource_path, self.readme)

    def _get_go_back_template(self):
        return (
            f"\n"
            f"{TEMPLATE_HORIZONTAL_LINE}{TEMPLATE_GO_BACK}\n\n{TEMPLATE_HORIZONTAL_LINE}"
            f"\n"
        )

    def generate(self):
        raise NotImplementedError

    def generate_readme(self):
        with open(f"{self.directory_path}/README.md", "w") as f:
            if self.go_back:
                f.write(self._get_go_back_template())
            f.write(f"{self.readme}\n\n")


class ConfigParentNode(ConfigNodeBaseClass):
    def __init__(self, node_name: str, config_data: dict, index: int = 0):
        super().__init__(node_name, config_data, index)
        self.contents = config_data.get("contents")

    def generate(self):
        print(f"Generating {self.node_name} directory...")
        os.makedirs(self.directory_path, exist_ok=True)
        for index, (child_node_name, child_node_data) in enumerate(self.contents.items()):
            config_child_node = ConfigChildNode(
                node_name=child_node_name,
                config_data=child_node_data,
                parent_dir=self.directory_path,
                index=index,
            )
            config_child_node.generate()
        self.generate_readme()


class ConfigChildNode(ConfigNodeBaseClass):

    def __init__(self, node_name: str, config_data: dict, parent_dir: str, index: int = 0):
        super().__init__(node_name, config_data, index)
        self.parent_dir = parent_dir
        self.directory_path = f"{self.parent_dir}/{self.index}0_{self.node_name}"

    def generate(self):
        print(f"Generating [{self.node_name}] directory...")
        os.makedirs(self.directory_path, exist_ok=True)
        self.generate_readme()


class MainStructure:
    def __init__(self, structure: dict):
        self.structure = structure

    def generate(self):
        for index, (directory_name, configuration) in enumerate(self.structure.items()):
            config_parent_node = ConfigParentNode(
                node_name=directory_name,
                config_data=configuration,
                index=index,
            )
            config_parent_node.generate()


def main():
    main_structure = MAIN_CONFIG_DATA.get("structure")
    main_structure_instance = MainStructure(main_structure)
    main_structure_instance.generate()


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    main()
