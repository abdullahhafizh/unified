import win32print
import os
import json

PRINTER_ERROR_STATES = (
    win32print.PRINTER_STATUS_NO_TONER,
    win32print.PRINTER_STATUS_NOT_AVAILABLE,
    win32print.PRINTER_STATUS_OFFLINE,
    win32print.PRINTER_STATUS_OUT_OF_MEMORY,
    win32print.PRINTER_STATUS_OUTPUT_BIN_FULL,
    win32print.PRINTER_STATUS_PAGE_PUNT,
    win32print.PRINTER_STATUS_PAPER_JAM,
    win32print.PRINTER_STATUS_PAPER_OUT,
    win32print.PRINTER_STATUS_PAPER_PROBLEM,
)

ERROR_PRINTER = {
    16: 'OUT_OF_PAPER'
}


def check_error(printer, error_states=PRINTER_ERROR_STATES):
    prn_opts = win32print.GetPrinter(printer)
    print("[DUMP] Printer Option: ", str(type(prn_opts)), json.dumps(prn_opts))
    status_opts = prn_opts[18]
    result = None
    for error in error_states:
        print("[DEBUG] Check Printer Error: ", str(error))
        if status_opts & error:
            print("[WARNING] Match Printer Error: ", str(status_opts), str(error))
            result = error
    return result


def main():
    printer_name = win32print.GetDefaultPrinter()
    print("[INFO] Printer Name: ", printer_name)
    prn = win32print.OpenPrinter(printer_name)
    error = check_error(prn)
    if error is not None:
        print("[ERROR] Found Printer Error: ", error)
    else:
        print("PRINTER OK")
        #  Do the real work
    win32print.ClosePrinter(prn)


if __name__ == "__main__":
    main()
