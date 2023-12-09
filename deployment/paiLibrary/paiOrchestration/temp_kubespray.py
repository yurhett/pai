# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import time
import yaml
import shutil
import logging
import tempfile

from ..common import linux_shell


class TempKubespray:

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._tmp_dir = tempfile.mkdtemp(prefix='.kubespray-', dir=tempfile.gettempdir())
        self._clone_kubespray()
        self._modify_files()

    def _clone_kubespray(self):
        self._logger.info("Begin to clone Kubespray 2.11 from GitHub")
        linux_shell.execute_shell_raise(
            shell_cmd="git clone -b release-2.11 https://github.com/yurhett/kubespray.git {}".format(self._tmp_dir),
            error_msg="Failed to clone Kubespray 2.11 from GitHub"
        )

    def _modify_files(self):
        # Modify `kubespray/remove-node.yml` to make ansible gather system information automatically
        self._logger.info("Modify `kubespray/remove-node.yml`, set `gather_facts: yes`")
        with open(os.path.join(self._tmp_dir, "remove-node.yml"), "r") as f1:
            data1 = yaml.load(f1, yaml.SafeLoader)
        data1[3]['gather_facts'] = True
        with open(os.path.join(self._tmp_dir, "remove-node.yml"), "w") as f1:
            yaml.dump(data1, f1, default_flow_style=False)

        # Modify `kubespray/roles/remove-node/post-remove/tasks/main.yml` to avoid the task `post-remove` failing
        self._logger.info("Modify `kubespray/roles/remove-node/post-remove/tasks/main.yml`, remove `run_once: true`")
        with open(os.path.join(self._tmp_dir, "roles/remove-node/post-remove/tasks/main.yml"), "r") as f2:
            data2 = yaml.load(f2, yaml.SafeLoader)
        del data2[2]['run_once']
        with open(os.path.join(self._tmp_dir, "roles/remove-node/post-remove/tasks/main.yml"), "w") as f2:
            yaml.dump(data2, f2, default_flow_style=False)

    def __del__(self):
        self._logger.info("Remove temporary downloaded Kubespray folder")
        try:
            shutil.rmtree(self._tmp_dir)
        except Exception as e:
            self._logger.error(str(e))
            self._logger.error("Failed to remove temporary downloaded Kubespray folder: {}, please remove it manually".format(self._tmp_dir))

    def get_folder_path(self):
        return self._tmp_dir
