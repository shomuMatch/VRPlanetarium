import csv
import math
import svgwrite
import cairosvg

SCALE = 40.0
RADIUS = 2.0


def calcDirection(ra, dec):
    raDeg = 360.0 / 24.0 * (float(ra[0]) + float(ra[1]) / 60.0 + float(ra[2]) / 3600.0)
    decDeg = float(dec[0]) + float(dec[1]) / 60.0 + float(dec[2]) / 3600.0
    return raDeg * SCALE, (decDeg + 90.0) * SCALE


# https://en.wikipedia.org/wiki/Color_index
def calcTemperature(bvIndex):
    return 4600.0 * (1.0 / (0.92 * bvIndex + 1.7) + 1.0 / (0.92 * bvIndex + 0.62))


# https://en.wikipedia.org/wiki/Planckian_locus
def calcCIECoord(t):
    x = 0.0
    y = 0.0
    if t < 1667.0:
        raise Exception
    elif t < 4000.0:
        x = -0.2661239e9 / t**3 - 0.2343589e6 / t**2 + 0.8776956e3 / t + 0.179910
    elif t < 25000.0:
        x = -3.0258469e9 / t**3 + 2.1070379e6 / t**2 + 0.2226347e3 / t + 0.240390
    else:
        raise Exception
    if t < 1667.0:
        raise Exception
    elif t < 2222.0:
        y = -1.1063814 * x**3 - 1.34811020 * x**2 + 2.18555832 * x - 0.20219683
    elif t < 4000.0:
        y = -0.9549476 * x**3 - 1.37418593 * x**2 + 2.09137015 * x - 0.16748867
    elif t < 25000.0:
        y = 3.0817580 * x**3 - 5.87338670 * x**2 + 3.75112997 * x - 0.37001483
    else:
        raise Exception
    return x, y


# https://www.cs.rit.edu/~ncs/color/t_convert.html#RGB%20to%20XYZ%20&%20XYZ%20to%20RGB
def calcRGB(x, y):
    X = x / y
    Y = 1.0
    Z = (1.0 - x - y) / y
    R = max(min(3.240970 * X - 1.537383 * Y - 0.498611 * Z, 1.0), 0.0) * 100.0
    G = max(min(-0.969244 * X + 1.875968 * Y + 0.041555 * Z, 1.0), 0.0) * 100.0
    B = max(min(0.055630 * X - 0.203977 * Y + 1.056972 * Z, 1.0), 0.0) * 100.0
    return R, G, B


# ガンマ補正
def gammaCorrection(x, gammaParameter):
    return 100 * (x / 100) ** (1.0 / gammaParameter)


def brightnessCorrection(r, g, b, magnitude, gammaParameter, brightnessParameter):
    magnitudeCoefficient = (
        brightnessParameter ** (-1 * (magnitude + 1.45)) / max(r, g, b) * 100
    )
    return (
        gammaCorrection(r * magnitudeCoefficient, gammaParameter),
        gammaCorrection(g * magnitudeCoefficient, gammaParameter),
        gammaCorrection(b * magnitudeCoefficient, gammaParameter),
    )


def calcColor(bvIndex, magnitude, gammaParameter, brightnessParameter):
    t = calcTemperature(float(bvIndex))
    x, y = calcCIECoord(t)
    R, G, B = calcRGB(x, y)
    return brightnessCorrection(
        R, G, B, float(magnitude), gammaParameter, brightnessParameter
    )


def calcMagnitude(magnitude):
    return float(magnitude)


def calcRadius(magnitude, decDeg):
    rv = RADIUS * 1.1 ** (1.45 - calcMagnitude(magnitude))
    rh = rv / math.cos(math.radians(decDeg / SCALE - 90.0))
    return rv, rh


def main(gammaParameter, brightnessParameter):
    filename = "texture" + str(gammaParameter) + "_" + str(brightnessParameter)
    dwg = svgwrite.Drawing(
        "svg/" + filename + ".svg",
        size=(360 * SCALE, 180 * SCALE),
        profile="full",
    )
    dwg.add(dwg.rect((0, 0), (360 * SCALE, 180 * SCALE), fill="black"))
    with open("hip.csv") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # print(row)
            try:
                raDeg, decDeg = calcDirection(row[1].split(" "), row[2].split(" "))
                r, g, b = calcColor(row[4], row[3], gammaParameter, brightnessParameter)
                rv, rh = calcRadius(row[3], decDeg)
                # print(raDeg, decDeg, r, g, b, rv, rh)
                # exit()
                dwg.add(
                    dwg.ellipse(
                        center=(raDeg, decDeg),
                        r=(rh, rv),
                        fill=svgwrite.rgb(r, g, b, "%"),
                    )
                )
            except Exception as e:
                # print(e)
                continue
    dwg.save()
    cairosvg.svg2png(
        url="svg/" + filename + ".svg", write_to="png/" + filename + ".png"
    )


if __name__ == "__main__":
    main(3.9, 2.5)
