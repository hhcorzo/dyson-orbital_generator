def st_to_sci(n: int) -> float:
    """Transform string to scientific notation"""
    return "%.8E" % float(n)


def chunks(lst: list, n: int) -> iter:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def orbital_split(lts: list, nbasis: int, nbuse: int) -> dict:
    """This routine generate the dictionaries for the creation of the Dyson orbitals"""
    orbs = {}
    for i, x in enumerate(chunks(lts, nbasis), 1):
        if len(x) == nbasis:
            orbs[i] = x
        else:
            sys.exit("Orbital", i, "has less elements than nbasis")
    if len(orbs) != nbuse:
        sys.exit("Number of orbitals extracted no equal to Nbuse")
    return orbs


def orb_extraction_info(filename1: str) -> tuple:
    """ This routine extract the orbitals from the SCF"""
    NBasis = 0
    NBuse = 0
    with open(filename1, "r") as fila:
        for line in fila:
            if "Number of basis functions" in line:
                words = line.split()
                for i in words:
                    for letter in i:
                        if letter.isdigit():
                            NBasis = NBasis * 10 + int(letter)
            elif "Number of independent functions" in line:
                words = line.split()
                for i in words:
                    for letter in i:
                        if letter.isdigit():
                            NBuse = NBuse * 10 + int(letter)
            if NBasis > 0 and NBuse > 0:
                return NBasis, NBuse


def amp_extraction_info(filename2: str) -> tuple:
    """This routine extracts the basis and orbital information from the  file with the  Feynman-Dyson"""
    NBasis = 0
    NBuse = 0
    with open(filename2, "r") as origin:
        for line in origin:
            if "NBasis=" in line:
                words = line.split()
                # print(words)
                NBasis = int(words[1])
                if words[6] == "NFC=":
                    NFC = int(words[7])
            elif "NROrb=" in line:
                words = line.split()
                NBuse = int(words[1])
            if NBasis > 0 and NBuse > 0:
                return NBasis, NBuse, NFC
