from colorclass import Color


class ColorText:

    @staticmethod
    def red(textToColor):
        return Color('{autored}' + str(textToColor) + '{/autored}')

    @staticmethod
    def green(textToColor):
        return Color('{autogreen}' + str(textToColor) + '{/autogreen}')

    @staticmethod
    def yellow(textToColor):
        return Color('{autoyellow}' + str(textToColor) + '{/autoyellow}')

    @staticmethod
    def blue(textToColor):
        return Color('{autoblue}' + str(textToColor) + '{/autoblue}')

    @staticmethod
    def cyan(textToColor):
        return Color('{autocyan}' + str(textToColor) + '{/autocyan}')

    @staticmethod
    def magenta(textToColor):
        return Color('{automagenta}' + str(textToColor) + '{/automagenta}')

    @staticmethod
    def black(textToColor):
        return Color('{autoblack}' + str(textToColor) + '{/autoblack}')

    @staticmethod
    def white(textToColor):
        return Color('{autowhite}' + str(textToColor) + '{/autowhite}')