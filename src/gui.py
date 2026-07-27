import flet as ft
from main_window import PyeducApp

def main_app(page: ft.Page):
    """
    Entry point for the Pyeduc Flet Application.
    The monolithic architecture has been refactored into the PyeducApp orchestrator
    and component modules under src/ui/.
    """
    PyeducApp(page)
