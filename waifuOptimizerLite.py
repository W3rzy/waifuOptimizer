#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import shutil
import tempfile
import ctypes
import time
import glob
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

IS_PY = not getattr(sys, 'frozen', False)
if IS_PY and not is_admin():
    run_as_admin()
    sys.exit(0)

try:
    import psutil
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "-q"], capture_output=True)
    import psutil

BG       = "#0d0d0d"
ACCENT   = "#e91e8c"
ACCENT2  = "#ff6ec7"
TEXT     = "#ffffff"
SUBTEXT  = "#888888"

# ===== РАСШИРЕННЫЙ СПИСОК ПРОЦЕССОВ ДЛЯ ЗАКРЫТИЯ =====
PROCESSES_TO_KILL = [
    # Браузеры и мессенджеры
    "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe",
    "steam.exe", "steamwebhelper.exe", "epicgameslauncher.exe", "discord.exe",
    "spotify.exe", "slack.exe", "zoom.exe", "teams.exe", "skype.exe", "telegram.exe",

    # Игровые клиенты и игры
    "csgo.exe", "cs2.exe", "VALORANT-Win64-Shipping.exe", "r5apex.exe",
    "Overwatch.exe", "RainbowSix.exe", "League of Legends.exe",
    "dota2.exe", "RocketLeague.exe", "TslGame.exe", "EscapeFromTarkov.exe",
    "cod.exe", "FortniteClient-Win64-Shipping.exe", "Cyberpunk2077.exe",
    "GTA5.exe", "RDR2.exe", "EldenRing.exe", "bf2042.exe", "bfv.exe",
    "Minecraft.Windows.exe", "RustClient.exe", "GenshinImpact.exe",
    "RobloxPlayerBeta.exe", "RobloxStudioLauncher.exe", "Roblox.exe", "RobloxCrashHandler.exe",

    # Аудио/видео и периферия
    "Voicemod.exe", "voicemod-v3.exe", "VoicemodV3.exe",
    "obs64.exe", "obs32.exe",
    "SoundCloud.exe",
    "EqualizerAPO.exe", "EqualizerAPOConfig.exe", "EqualizerAPODeviceSelector.exe",

    # Xbox и игровые панели
    "XboxApp.exe", "XboxPcAppFT.exe", "XboxPcAppCE.exe", "XboxPcAppAdminServer.exe",
    "XboxPcApp.exe", "XboxPartyChatHost.exe", "XboxGameBarWidgets.exe",
    "XboxGameBar.exe", "XboxGameCallableUI.exe",

    # Системные утилиты и приложения (добавлены новые)
    "GameAssist.exe", "GameAssistService.exe",
    "ShellBagAnalyzer.exe", "shellbag_analyzer.exe",
    "happd.exe", "happd", "happ-tcping.exe",
    "HPAppHelper.exe", "HP.HPAppHelper.exe",
    "OneDrive.exe", "GameBar.exe", "Widgets.exe",
    "Microsoft.Photos.exe", "ScreenClippingHost.exe", "MicrosoftEdgeUpdate.exe",
    "GoogleUpdate.exe", "NvContainer.exe", "NvTelemetryContainer.exe", "AMDRSServ.exe",

    # Windows-приложения (UWP и классические) – добавлены новые
    "SearchApp.exe",                  # поиск Windows
    "YourPhone.exe",                  # Ваш телефон
    "PhoneExperienceHost.exe",        # хост телефона
    "SkypeApp.exe",                   # Skype (UWP)
    "Maps.exe",                       # Карты
    "Weather.exe",                    # Погода
    "News.exe",                       # Новости
    "MicrosoftEdge.exe",              # Edge (если не используется)
    "MicrosoftEdgeCP.exe",            # вспомогательный процесс Edge
    "MicrosoftEdgeSH.exe",            # ещё один процесс Edge
    "Calculator.exe",                 # Калькулятор
    "WindowsTerminal.exe",            # Терминал
    "PowerShell.exe",                 # PowerShell
    "cmd.exe",                        # командная строка
    "Microsoft.MicrosoftStickyNotes.exe",  # Стикеры
    "Microsoft.WindowsCamera.exe",         # Камера
    "Microsoft.ZuneMusic.exe",             # Музыка Groove
    "Microsoft.ZuneVideo.exe",             # Видео Groove
    "Microsoft.People.exe",                # Контакты
    "Microsoft.MSPaint.exe",               # Paint 3D
    "Microsoft.Office.OneNote.exe",        # OneNote (UWP)
    "WinStore.App.exe",                    # Магазин Windows
    "Microsoft.StorePurchaseApp.exe",      # Покупки в магазине
    "SystemSettings.exe",                  # Параметры (если открыто)
    "backgroundTaskHost.exe",              # хост фоновых задач (иногда можно закрыть)
    "wermgr.exe",                          # отчёт об ошибках
    "werfault.exe",                        # обработчик ошибок
]

# ===== СЛУЖБЫ ДЛЯ ОТКЛЮЧЕНИЯ (уже расширены ранее) =====
SERVICES_TO_STOP = [
    "WerSvc", "seclogon", "Browser", "MapsBroker",
    "RetailDemo", "RemoteRegistry",
    "vmms", "vmic", "hvs", "vmbus",
    "NvStereo",
    "DiagTrack", "lfsvc",
    "XblAuthManager", "XblGameSave", "XboxNetApiSvc",
    "XboxGipSvc", "XboxLiveNetworking",
    "WpnService", "PcaSvc", "DPS",
    "WdiServiceHost", "WdiSystemHost",
    "CscService", "TrkWks", "TapiSrv", "AJRouter",
    "WpcMonSvc", "SCardSvr", "ScDeviceEnm", "WbioSrvc",
    "SystemUsageReportSvc_QUEENCREEK", "AUEPLauncher",
    "gupdate", "gupdatem", "Razer Game Scanner Service",
    "LogiRegistryService", "NvEnergy", "amdacp3x",
    "WalletService", "WMPNetworkSvc", "SharedAccess",
    "WinHttpAutoProxySvc", "ALG", "SensorService",
    "SensrSvc", "dmwappushservice", "diagnosticshub.standardcollector.service",
    "BcastDVRUserService", "GameDVR", "GameBarPresenceWriter",
]

# Критические службы – не трогаем
CRITICAL_SERVICES = {
    "RpcSs", "DcomLaunch", "EventLog", "PlugPlay", "Power", "SystemEventsBroker",
    "LSM", "Winmgmt", "nsi", "Dnscache", "Dhcp", "BFE", "mpssvc", "ProfSvc",
    "UserManager", "StateRepository", "LicenseManager", "BrokerInfrastructure",
    "SvcHost", "TimeBroker", "TimeBrokerSvc", "Wcmsvc", "NlaSvc", "Netman",
    "WlanSvc", "wwansvc", "WwanSvc", "Ndis", "Tcpip", "AFD",
    "Schedule", "Themes", "TermService", "Appinfo",
    "wuauserv", "UsoSvc", "WaaSMedicSvc",
    "NvContainer", "NvTelemetryContainer", "NvDisplayContainer", "NvContainerLocalSystem",
    "AMDRSServ", "amdlog", "AMD External Events Utility", "AMD Crash Defender Service",
    "amdfendr", "amdfendrmgr", "AMDACP", "AMD Link Hub",
    "storahci", "stornvme", "disk", "partmgr", "volmgr",
    "PrintSpooler", "RemoteAccess",
    "jhi_service", "LMS", "Intel(R) TPM Provisioning Service",
    "igccservice", "cplspcon", "igfxCUIService2.0.0.0",
    "Dptf", "esifsvc", "esif_vsec", "XTU3SERVICE",
    "WSearch", "SysMain",
    "TabletInputService",
    "OpenVPNService", "WindscribeService", "ProtonVPNService",
    "NordVPNService", "ExpressVPNService",
}
SERVICES_TO_STOP = [s for s in SERVICES_TO_STOP if s not in CRITICAL_SERVICES]

def safe_run(cmd):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, shell=True, capture_output=True, timeout=10,
                       startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def service_exists(svc):
    result = subprocess.run(f'sc query "{svc}"', shell=True, capture_output=True, text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    return "SERVICE_NAME" in result.stdout

def kill_processes():
    for proc in PROCESSES_TO_KILL:
        if proc.lower() == "javaw.exe":
            continue
        if proc.lower() == "discord.exe":
            for p in psutil.process_iter(['pid', 'name', 'memory_info']):
                if p.info['name'] and p.info['name'].lower() == "discord.exe":
                    try:
                        if p.info['memory_info'].rss / (1024 * 1024) > 300:
                            continue
                    except:
                        pass
        safe_run(f"taskkill /F /IM {proc}")

def stop_services():
    stopped = []
    for svc in SERVICES_TO_STOP:
        if service_exists(svc):
            safe_run(f'sc stop "{svc}"')
            time.sleep(0.02)
            safe_run(f'sc config "{svc}" start= disabled')
            stopped.append(svc)
    return stopped

def clean_temp_files():
    temp_dir = tempfile.gettempdir()
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)
    except:
        pass
    sys_temp = os.path.join(os.environ['SystemRoot'], 'Temp')
    try:
        shutil.rmtree(sys_temp, ignore_errors=True)
        os.makedirs(sys_temp, exist_ok=True)
    except:
        pass
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0001)
    except:
        pass
    for pattern in [
        os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Edge\\User Data\\Default\\Cache\\*'),
        os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data\\Default\\Cache\\*'),
    ]:
        for p in glob.glob(pattern):
            try:
                shutil.rmtree(p, ignore_errors=True)
            except:
                pass

def clean_startup():
    run_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]
    startup_blacklist = [
        "OneDrive", "Discord", "Spotify", "Steam", "EpicGamesLauncher",
        "MicrosoftEdgeAutoLaunch", "GoogleUpdate", "XboxApp",
        "Voicemod", "GameAssist", "Roblox", "Slack", "Zoom", "Teams", "Skype",
        "Telegram", "WhatsApp", "Signal", "Viber", "Outlook", "Microsoft.Photos",
        "ScreenClippingHost", "Widgets", "GameBar", "NvContainer", "AMDRSServ",
        "HPAppHelper", "happd", "obs64", "obs32", "SoundCloud",
        "EqualizerAPO", "EqualizerAPOConfig", "EqualizerAPODeviceSelector",
    ]
    backup_path = os.path.join(os.path.expanduser("~"), "Desktop", "Waifu_Startup_Backup.reg")
    try:
        safe_run(f'reg export "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" "{backup_path}" /y')
        safe_run(f'reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "{backup_path}" /y')
        safe_run(f'reg export "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run" "{backup_path}" /y')
    except:
        pass

    for hive, key_path in run_paths:
        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
                i = 0
                while True:
                    try:
                        name, value, typ = winreg.EnumValue(key, i)
                        for black in startup_blacklist:
                            if name.lower() == black.lower() or name.lower().startswith(black.lower() + "."):
                                winreg.DeleteValue(key, name)
                                break
                        i += 1
                    except OSError:
                        break
        except:
            pass

    startup_folders = [
        os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.join(os.environ['PROGRAMDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup"),
    ]
    for folder in startup_folders:
        if os.path.exists(folder):
            for item in os.listdir(folder):
                base_name = os.path.splitext(item)[0]
                for black in startup_blacklist:
                    if base_name.lower() == black.lower():
                        try:
                            os.remove(os.path.join(folder, item))
                        except:
                            pass
                        break

def block_telemetry_hosts():
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    entries = [
        "0.0.0.0 oca.telemetry.microsoft.com",
        "0.0.0.0 oca.microsoft.com",
        "0.0.0.0 kmwatsonc.events.data.microsoft.com",
        "0.0.0.0 v10.vortex-win.data.microsoft.com",
        "0.0.0.0 settings-win.data.microsoft.com",
        "0.0.0.0 watson.telemetry.microsoft.com",
        "0.0.0.0 vortex.data.microsoft.com",
        "0.0.0.0 telemetry.microsoft.com",
        "0.0.0.0 sqm.telemetry.microsoft.com",
        "0.0.0.0 pre.footprintpredict.com",
        "0.0.0.0 i1.services.social.microsoft.com",
        "0.0.0.0 i1.services.social.microsoft.com.nsatc.net",
    ]
    try:
        with open(hosts_path, "r") as f:
            content = f.read()
        with open(hosts_path, "a") as f:
            for entry in entries:
                if entry not in content:
                    f.write(entry + "\n")
    except:
        pass

def disable_telemetry_tasks():
    tasks = [
        r"\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
        r"\Microsoft\Windows\Application Experience\ProgramDataUpdater",
        r"\Microsoft\Windows\Application Experience\StartupAppTask",
        r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
        r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
        r"\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
        r"\Microsoft\Windows\Feedback\Siuf\DmClient",
        r"\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
        r"\Microsoft\Windows\Flighting\FeatureConfig\UsageDataReporting",
        r"\Microsoft\Windows\Windows Error Reporting\QueueReporting",
    ]
    for task in tasks:
        safe_run(f'schtasks /Change /TN "{task}" /Disable')

def configure_power():
    safe_run('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c')
    safe_run('powercfg -h off')

def create_restore_point():
    safe_run('powershell -Command "Enable-ComputerRestore -Drive \'C:\' -ErrorAction SilentlyContinue"')
    safe_run('sc config vss start= demand')
    safe_run('net start vss')
    safe_run('powershell -Command "Checkpoint-Computer -Description \'Waifu Optimizer Restore Point\' -RestorePointType \'MODIFY_SETTINGS\'"')

def create_change_log(stopped_services):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    log_path = os.path.join(desktop, "Waifu_Optimizer_Changes.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("Waifu Optimizer — список изменений\n")
            f.write("=" * 50 + "\n")
            f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if stopped_services:
                f.write("Отключённые службы:\n")
                for svc in stopped_services:
                    f.write(f"  - {svc}\n")
            else:
                f.write("Службы не отключались.\n")
            f.write("\nОчищена автозагрузка.\n")
            f.write("Заблокированы телеметрические хосты.\n")
            f.write("Отключены задачи планировщика.\n")
            f.write("\nДля отката изменений используйте кнопку «Сброс» в программе\n")
            f.write("или восстановите систему через точку восстановления.\n")
        return log_path
    except:
        return None

def full_clean(stop_services_flag, performance_tweaks_flag):
    create_restore_point()
    kill_processes()
    stopped_services = []
    if stop_services_flag:
        stopped_services = stop_services()
    clean_temp_files()
    clean_startup()
    block_telemetry_hosts()
    disable_telemetry_tasks()
    if performance_tweaks_flag:
        configure_power()
    create_change_log(stopped_services)
    return stopped_services

def reset_to_default(stopped_services):
    if stopped_services:
        for svc in stopped_services:
            if service_exists(svc):
                safe_run(f'sc config "{svc}" start= auto')
                safe_run(f'sc start "{svc}"')
    tasks = [
        r"\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
        r"\Microsoft\Windows\Application Experience\ProgramDataUpdater",
        r"\Microsoft\Windows\Application Experience\StartupAppTask",
        r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
        r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
        r"\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
        r"\Microsoft\Windows\Feedback\Siuf\DmClient",
        r"\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
        r"\Microsoft\Windows\Flighting\FeatureConfig\UsageDataReporting",
        r"\Microsoft\Windows\Windows Error Reporting\QueueReporting",
    ]
    for task in tasks:
        safe_run(f'schtasks /Change /TN "{task}" /Enable')
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        with open(hosts_path, "r") as f:
            lines = f.readlines()
        with open(hosts_path, "w") as f:
            for line in lines:
                if "0.0.0.0" not in line or "telemetry" not in line.lower():
                    f.write(line)
    except:
        pass
    backup_path = os.path.join(os.path.expanduser("~"), "Desktop", "Waifu_Startup_Backup.reg")
    if os.path.exists(backup_path):
        safe_run(f'reg import "{backup_path}"')
    safe_run('ipconfig /flushdns')
    safe_run('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e')
    safe_run('powercfg -h on')
    messagebox.showinfo("Сброс", "Все настройки возвращены к исходным.\nРекомендуется перезагрузить компьютер.")

class WaifuOptimizer(tk.Tk):
    _stages = [
        ("Создание точки восстановления...", ""),
        ("Закрытие фоновых процессов...", ""),
        ("Очистка временных файлов...", ""),
        ("Очистка автозагрузки...", ""),
        ("Оптимизация системы...", ""),
        ("Готово!", "Нажмите Остановить"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Waifu Optimizer")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.geometry("440x380")
        self._step = 0
        self._done = False
        self._stopped_services = []
        self._build_ui()

    def _build_ui(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.place(relwidth=1, relheight=1)

        tk.Label(self.main, text="✦", bg=BG, fg=ACCENT, font=("Segoe UI", 30, "bold")).pack(pady=(20, 0))
        tk.Label(self.main, text="Waifu Optimizer", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(pady=(2, 5))
        tk.Label(self.main, text="Выберите режим и нажмите Старт", bg=BG, fg=SUBTEXT, font=("Segoe UI", 10)).pack(pady=(0, 10))

        self.var_services = tk.BooleanVar(value=True)
        chk1 = tk.Checkbutton(self.main, text="Отключать службы (рекомендуется)",
                              variable=self.var_services,
                              bg=BG, fg=TEXT, selectcolor=BG, font=("Segoe UI", 10), anchor="w")
        chk1.pack(pady=(2, 0), padx=22, anchor="w")

        self.var_performance = tk.BooleanVar(value=True)
        chk2 = tk.Checkbutton(self.main, text="Оптимизация Windows (схема питания, производительность)",
                              variable=self.var_performance,
                              bg=BG, fg=TEXT, selectcolor=BG, font=("Segoe UI", 10), anchor="w")
        chk2.pack(pady=(2, 5), padx=22, anchor="w")

        btn_frame = tk.Frame(self.main, bg=BG)
        btn_frame.pack(fill="x", padx=22, pady=(5, 10))

        self.btn_start = tk.Button(btn_frame, text="▶ Старт", command=self._start,
                                   bg=ACCENT, fg=TEXT, activebackground=ACCENT2,
                                   relief="flat", font=("Segoe UI", 12, "bold"), height=2)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_reset = tk.Button(btn_frame, text="↺ Сброс", command=self._reset,
                                   bg=ACCENT, fg=TEXT, activebackground=ACCENT2,
                                   relief="flat", font=("Segoe UI", 12, "bold"), height=2)
        self.btn_reset.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.anim = tk.Frame(self, bg=BG)
        center = tk.Frame(self.anim, bg=BG)
        center.place(relx=0.5, rely=0.4, anchor="center")
        self.icon = tk.Label(center, text="✦", bg=BG, fg=ACCENT, font=("Segoe UI", 38, "bold"))
        self.icon.pack()
        self.status = tk.Label(center, text="", bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold"))
        self.status.pack(pady=(8, 0))
        self.sub = tk.Label(center, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 10))
        self.sub.pack(pady=(4, 0))

        self.btn_stop = tk.Button(self.anim, text="Остановить", command=self._stop,
                                  bg=ACCENT, fg=TEXT, activebackground=ACCENT2,
                                  relief="flat", font=("Segoe UI", 11, "bold"), height=2)
        self.btn_stop.place(relx=0, rely=1, anchor="sw", relwidth=1, height=46, y=0)
        self.btn_stop.place_forget()

        self.done_frame = tk.Frame(self, bg=BG)
        center2 = tk.Frame(self.done_frame, bg=BG)
        center2.place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(center2, text="✦", bg=BG, fg=ACCENT, font=("Segoe UI", 38, "bold")).pack()
        tk.Label(center2, text="Оптимизация завершена", bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(pady=(8, 0))
        tk.Label(center2, text="Нажмите «Закрыть»", bg=BG, fg=SUBTEXT, font=("Segoe UI", 10)).pack(pady=(4, 0))
        tk.Button(self.done_frame, text="Закрыть", command=self.destroy,
                  bg=ACCENT, fg=TEXT, activebackground=ACCENT2,
                  relief="flat", font=("Segoe UI", 11, "bold"), height=2).place(relx=0, rely=1, anchor="sw", relwidth=1, height=46, y=0)

        self._show(self.main)

    def _show(self, frame):
        for f in (self.main, self.anim, self.done_frame):
            f.place_forget()
        frame.place(relwidth=1, relheight=1)

    def _start(self):
        self._show(self.anim)
        self.btn_stop.place_forget()
        self._step = 0
        self._done = False
        self.status.config(text="")
        self.sub.config(text="")
        threading.Thread(target=self._run, daemon=True).start()
        self._update()

    def _run(self):
        self._stopped_services = full_clean(
            self.var_services.get(),
            self.var_performance.get()
        )
        self._done = True

    def _update(self):
        if self._step < len(self._stages):
            text, sub = self._stages[self._step]
            self.status.config(text=text)
            self.sub.config(text=sub)
            self._step += 1
            self._pulse()
            self.after(1200, self._update)
        else:
            if self._done:
                self.sub.config(text="Нажмите «Остановить»")
                self.btn_stop.place(relx=0, rely=1, anchor="sw", relwidth=1, height=46, y=0)
            else:
                self.sub.config(text="Завершение...")
                self.after(500, self._update)

    def _pulse(self):
        self.icon.config(fg=SUBTEXT)
        self.after(200, lambda: self.icon.config(fg=ACCENT))

    def _stop(self):
        self._show(self.done_frame)

    def _reset(self):
        if messagebox.askyesno("Сброс", "Вернуть все настройки к исходным?"):
            threading.Thread(target=reset_to_default, args=(self._stopped_services,), daemon=True).start()

class InstallerWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Waifu Optimizer")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.geometry("380x180")
        tk.Label(self, text="✦", bg=BG, fg=ACCENT, font=("Segoe UI", 30, "bold")).pack(pady=(16, 0))
        tk.Label(self, text="Waifu Optimizer", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(pady=(4, 14))
        self.btn = tk.Button(self, text="Установить", bg=ACCENT, fg=TEXT, activebackground=ACCENT2,
                             relief="flat", font=("Segoe UI", 11, "bold"), width=26, height=2, command=self._build)
        self.btn.pack()
        self.prog = ttk.Progressbar(self, length=280, mode="indeterminate", style="pink.Horizontal.TProgressbar")
        self.err = tk.Label(self, text="", bg=BG, fg="#ff5555", font=("Segoe UI", 8), wraplength=340)

    def _build(self):
        self.err.pack_forget()
        self.btn.config(state="disabled", text="Сборка...")
        self.prog.pack(pady=(10, 0))
        self.prog.start(12)
        threading.Thread(target=self._build_exe, daemon=True).start()

    def _build_exe(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "psutil", "-q"],
                           capture_output=True, check=True)
        except Exception as e:
            self._done(False, str(e))
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        out_dir = os.path.join(desktop, "Waifu Optimizer")
        os.makedirs(out_dir, exist_ok=True)
        script = os.path.abspath(__file__)
        work_dir = os.path.join(tempfile.gettempdir(), "_waifu_build")
        try:
            r = subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "--onefile", "--noconsole",
                "--name", "WaifuOptimizer",
                "--distpath", out_dir,
                "--workpath", work_dir,
                "--specpath", work_dir,
                script,
            ], capture_output=True, text=True)
            if r.returncode != 0:
                self._done(False, (r.stderr or r.stdout)[-900:])
                return
        except Exception as e:
            self._done(False, str(e))
            return
        exe_path = os.path.join(out_dir, "WaifuOptimizer.exe")
        if os.path.exists(exe_path):
            self._done(True, exe_path)
        else:
            self._done(False, "EXE не найден.")
        shutil.rmtree(work_dir, ignore_errors=True)

    def _done(self, ok, msg=""):
        self.prog.stop()
        self.prog.pack_forget()
        if ok:
            self.btn.config(state="normal", text="✓ Готово! Закрыть",
                            bg="#2e7d32", command=self.destroy)
            self.btn.bind("<Enter>", lambda e: None)
            self.btn.bind("<Leave>", lambda e: None)
            messagebox.showinfo("Успех", f"Файл создан:\n{msg}\n\nПапка: {os.path.dirname(msg)}")
        else:
            self.err.config(text=msg.strip())
            self.err.pack(pady=(8, 0), padx=16)
            self.geometry(f"380x360+{self.winfo_x()}+{self.winfo_y()}")
            self.btn.config(state="normal", text="Повторить", bg=ACCENT, command=self._build)
            self.btn.bind("<Enter>", lambda e: self.btn.config(bg=ACCENT2))
            self.btn.bind("<Leave>", lambda e: self.btn.config(bg=ACCENT))

if __name__ == "__main__":
    if IS_PY:
        InstallerWindow().mainloop()
    else:
        WaifuOptimizer().mainloop()