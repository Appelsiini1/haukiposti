#Haukiposti V0.0
#15.3.2020
# (c) Rami Saarivuori & Aarne Savolainen

try:
    import logging, os
    import emailFunc as mail
except Exception:
    exit(-1)
    

def main():
    logname = "haukilog.log"
    logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


if __name__ == "__main__":
    main()
