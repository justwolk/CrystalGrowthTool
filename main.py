import sys

from app.app import CrystalGrowthApplication


if __name__ == '__main__':
    app = CrystalGrowthApplication(sys.argv)
    sys.exit(app.exec_())
