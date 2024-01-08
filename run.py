"""
Програмний комплекс
управління графічним інтерфейсом
за допомогою технологій Eye Tracking
Кондратюк Наталії
ПІ-22-1м
"""

from modules.loggers import LoggerSetup

from modules.calibration import CalibrationApp
from modules.controller_app import Controller
from modules.game_bunny import GameSB
from modules.eye_track_controller_app import EyeTrackController
from modules.eye_track import EyeTracker

def main() :
    LoggerSetup().set_warning_logs().set_console_logs().set_logs_timetable()

    CalibrationApp()()
    Controller()()
    GameSB()()
    EyeTrackController()()
    EyeTracker()()

if __name__ == '__main__' :
    main()