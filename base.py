import main as tr
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon


def isInsideTriangle(point_to_check, vertex_A, vertex_B, vertex_C):
    # Creare un triangolo come istanza di Polygon con i vertici A, B e C
    triangle = Polygon([vertex_A[0], vertex_B[0], vertex_C[0]])
    # Utilizzare il metodo contains di Polygon per verificare se il punto è all'interno del triangolo
    return triangle.contains(point_to_check[0])

def draw_triangle_and_point(point_to_draw, vertex_A, vertex_B, vertex_C):
    # Creare un triangolo come istanza di Polygon con i vertici A, B e C
    triangle = Polygon([vertex_A[0], vertex_B[0], vertex_C[0]])
    # Creare il plot
    x, y = zip(*triangle.exterior.coords)
    plt.fill(x, y, 'g', alpha=0.2)  # Triangolo blu semi-trasparente
    plt.plot(point_to_draw[0].x, point_to_draw[0].y, 'ro')  # Punto rosso
    plt.xlim(min(x) - 0.01, max(x) + 0.01)
    plt.ylim(min(y) - 0.01, max(y) + 0.01)
    plt.show()
    return




if __name__ == '__main__':
    pointA = [tr.Point(9.156215, 45.580312), "Paderno"]
    pointB = [tr.Point(9.17231, 45.536827), "MJ"]
    m, q = tr.line_2_points(pointA, pointB)

    print(f"slope è:{m} e intecerpt:{q}")

    print(f"perfect slope per filotto è:{-1 / m}")
    # Esempio di utilizzo della funzione
    # Definire i vertici del triangolo e il punto da controllare
    vertex_A = [Point(9.156215, 45.580312), "Paderno"]
    vertex_B = [Point(9.17231, 45.536827), "MJ"]
    vertex_C = [Point(9.174951, 45.576114), "Bacheca informativa"]

    point_to_check = [Point(9.164932, 45.574097), "Consorzio"]

    # Chiamare la funzione e stampare il risultato
    inside = isInsideTriangle(point_to_check, vertex_A, vertex_B, vertex_C)
    if inside:
        draw_triangle_and_point(point_to_check, vertex_A, vertex_B, vertex_C)


