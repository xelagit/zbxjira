# -*- coding: utf-8 -*-
"""The clean command."""


from base import Base
import os


class Limpar(Base):
    """limpa o diretorio de cache e arquivos temporarios"""

    def run(self, acao=None):
        folder = self.conf['CACHE_DIR']
        self.log.info("Limpando o diretorio de cache" % folder)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    self.log.error("Removendo %s" % file_path)
                    os.unlink(file_path)
            except Exception as e:
                self.log.error(e)
