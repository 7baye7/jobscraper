#!/usr/bin/env python3

import os
import datetime
import itertools
from pathlib import Path
from logging import getLogger, Logger

from .utility import getSimpleModuleName


class FileManager:
    __folderToManagePath: str
    __logger: Logger

    def __init__(self, folderToManage: str):
        self.__folderToManagePath = folderToManage
        self.__logger = getLogger(getSimpleModuleName(__name__))

    def saveFile(self, fileName: str, extension: str, content: str) -> None:
        Path(self.__folderToManagePath).mkdir(parents=True, exist_ok=True)

        time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filePath = os.path.join(self.__folderToManagePath, '%s_%s.%s' % (fileName, time, extension))

        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.__logger.info('Exported content into file = "%s"', filePath)

    def deleteOldFiles(self, mask: str, filesToKeepCount: int) -> None:
        if not os.path.exists(self.__folderToManagePath):
            return
        
        files = list(Path(self.__folderToManagePath).glob(mask))
        files.sort(key = lambda path: path.stat().st_mtime, reverse = True) # st_mtime - last modification time in seconds
        filesToDelete = itertools.islice(files, filesToKeepCount, None)
        for file in filesToDelete:
            file.unlink()
            self.__logger.info('Deleted old file = "%s"', file.absolute())