# pylint: disable=no-member
import math
import numpy as np
import scipy.signal
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import PIL.Image as Image
import matplotlib

import pickle as pickle
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import cdist
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D


def aufgabe6():

    #
    # Bag-of-Features
    #
    # Bisher haben wir Bag-of-Words Repraesentationen auf natuerlichen Texten
    # betrachtet. Das Bag-of-Words Konzept laesst sich allerdings auch auf Bilder
    # uebertragen. Allgemeiner spricht man dann von Bag-of-Features. Dabei wird
    # die 'Bag' (also das Histogramm) nicht mehr ueber Wortstaemme gebildet sondern
    # ueber andere typische Merkmalsauspraegungen. 
    # http://arxiv.org/pdf/1101.3354.pdf (Introduction to the bag-of-features principle)
    #
    # Fuer Bilder haben sich in diesem Zusammenhang Merkmale etabliert, die auf
    # lokalen Bilddeskriptoren beruhen. Ein lokaler Bilddeskriptor liefert dabei
    # eine (numerische) Beschreibung der lokalen Nachbarschaft eines bestimmten Bildpunkts.
    #
    # Um die typischen lokalen Bilddeskriptoren fuer eine Problemdomaene (repraesentiert
    # durch einen Beispieldatensatz) zu finden, fuehrt man eine Clusteranalyse durch.
    # Die Clusterrepraesentanten sind dann die typischen Auspraegungen fuer die
    # Deskriptoren, die zu dem Cluster gehoeren. In Analogie zu dem Bag-of-Words
    # Ansatz nennt man sie auch Visual Words und die Menge aller Visual Words das
    # Visual Vocabulary.
    #
    # Moechte man eine Bag-of-Features Repraesentation eines Bildes berechnen,
    # berechnet man zunaechst Deskriptoren. Da es im Vorfeld nicht immer einfach
    # ist zu bestimmen welche Bildbereich relevant bzw nicht relevant sind, berechnet
    # man die Deskriptoren an den Punkten eines regelmaessigen Grids.
    # Jedem Deskriptor wird nun das aehnlichste Visual Word aus dem Visual Vocabulary
    # zugeordnet. Dies bezeichnet man als Quantisierung.
    # Die Bag-of-Features wird gebildet indem man das Histgramm ueber die Visual Words
    # in dem Bild bzw in einem Bildausschnitt berechnet. 
    #  
    # Erlaeutern Sie die Begriffe Visual Word und Visual Vocabulary mit Ihren eigenen
    # Worten. Stellen Sie die Analogie zwischen Bag-of-Words und Bag-of-Features
    # her:
    #
    # Bag-of-Words               Bag-of-Features
    # Wort                  ->   Punkte im Cluster
    # typische Wortstaemme  ->   lokale Bilddeskriptoren bzw Clusterzentroiden
    #
    #
    # -> Ein Visual Word ist ein Bereich aus Pixeln eines Bildes, aus dem sich Informationen, wie ein bestimmtes Merkmal
    # dieses Bereichs, herleiten lassen.
    #
    # -> Ein Visual Vocabulary ist die Menge aller Visual Words, die in dem Bild vorkommen.
    #
    # Welche Rolle spielt die Anordung der lokalen Bilddeskriptoren im regelmaessigen
    # Grid?
    # -> Erkennung von Kanten und damit der Abgrenzung zu einzelnen Wörtern und Buchstaben
    


    #
    # Lokale Bilddeskriptoren
    #
    # Ein beliebter lokaler Bilddeskriptor ist der SIFT (Scale Invariant Feature Transform)
    # Deskriptor. 
    # http://www.robots.ox.ac.uk/~vgg/research/affine/det_eval_files/lowe_ijcv2004.pdf
    # (siehe auch Vorlesung Computer Vision)
    # Das SIFT Verfahren besteht aus einem Schritt zur Detektion 'interessanter' 
    # lokaler Bildpunkte und einem Schritt zu deren Beschreibung (Deskriptor).
    # Da wir die Deskriptoren in einem regelmaessigen Grid berechnen werden, wird 
    # der Detektor hier nicht verwendet. 
    # Der Deskriptor basiert auf Statistiken (Histogrammen) von (lokalen) Bildgradienten.
    #   
    # Bildgradienten
    # Bei dem Bildgradienten handelt es sich um die (zweidimensionale) Ableitung der
    # Bildintensitaet (Grauwert) nach x und y. In der Praxis approximiert man ihn 
    # (diskretes Signal) durch spezielle Operatoren. Dieses Konzept soll 
    # zunaechst anhand eines eindimensionalen Beipiels verdeutlicht werden. 
    # Berechnen Sie die Kreuzkorrelation des Signals 
    # 0 0 0 1 2 3 4 5 0 0 9 3 0 0
    # mit der Maske 
    # -1 0 1
    # -> Ergebnis:
    crosscor = np.correlate([0, 0, 0, 1, 2, 3, 4, 5, 0, 0, 9, 3, 0, 0], [-1, 0, 1], mode="full")
    crosscor2 = np.correlate([0, 0, 0, 1, 2, 3, 4, 5, 0, 0, 9, 3, 0, 0], [-1, 0, 1], mode="same")
    crosscor3 = np.correlate([0, 0, 0, 1, 2, 3, 4, 5, 0, 0, 9, 3, 0, 0], [-1, 0, 1])
    print(str(crosscor))
    print(str(crosscor2))
    print(str(crosscor3))
    # Wie kann man die Randfaelle behandeln?
    # -> Je nach Positionierung der Maske (siehe Modi full, same und normal)
    # Diskutieren Sie Eigenschaften und Funktion des Filters (Hochpass).
    # -> Filter soll nur gravierende Veränderungen zulassen (z.B. von schwarz auf weiß) und weniger bedeutsame
    #   Veränderungen werden ignoriert (große Helligkeitsunterschiede)
    
    #
    # Der Operator laesst sich auf zweidimensionale diskrete Signale verallgemeinern.
    # Dabei benoetigt man eine Maske fuer horizontale Kanten und eine fuer
    # vertikale Kanten.
    # Zeigen Sie wie beide Masken durch geeignete Multiplikationen der Vektoren
    # [ -1 0 1] und [1 1 1] gebildet werden koennen. Es resultiert der sogenannte
    # Prewitt Operator.
    #
    # [-1 0 1].T * [1 1 1] = [ [-1 -1 -1]
    #                          [0  0  0]
    #                          [1  1  1] ]
    # und für horizontale Kanten dann transponieren
    #
    # In der Praxis konstruiert man den Operator haeufig mit dem Tiefpass Filter
    # [1 2 1]
    # Dabei ergibt sich der Sobel Operator. 
    # Berechnen Sie beide Masken des Sobel Operators. 
    # Diskutieren Sie den Unterschied zwischen Prewitt und Sobel.
    #
    #
    # [-1 0 1].T * [1 2 1] = [ [-1 -2 -1]
    #                          [0  0  0]
    #                          [1  2  1] ]
    # und für horizontale Kanten dann transponieren
    #
    # -> Der Sobel Operator gewichtet die mittleren Werte der Maske höher und der Prewitt Operator gewichtet die
    # Grauwerte gar nicht
    #
    # An folgendem Dokumentenabbild sollen der Sobel-Operator, lokale Bilddeskriptoren
    # und Bag-of-Features Repraesentionen erprobt werden. Es stehen zwei Versionen
    # zur Verfuegung. 2700270_small.png ist fuer eine performantere Ausfuehrung geeignet.
    # 2700270.png ist wesentlich hochaufloesender, so dass bestimmte Details besser
    # sichtbar werden. Bedenken Sie, dass bei der Verwendung von 2700270.png unter
    # Umstaenden die Deskriptorparameter (siehe unten) angepasst werden muessen.
    #
    document_image_filename = '2700270_small.png'
    image = Image.open(document_image_filename)
    # Fuer spaeter folgende Verarbeitungsschritte muss das Bild mit float32-Werten vorliegen. 
    im_arr = np.asarray(image, dtype='float32')
    # Die colormap legt fest wie die Intensitaetswerte interpretiert werden.
    plt.imshow(im_arr, cmap=cm.get_cmap('Greys_r'))
    #plt.show()
    #
    # Berechnen Sie das Ergebnis des Sobel-Operators mit der horizontalen und
    # vertikalen Maske. Visualisieren Sie die Ergebnisse und achten Sie
    # auf eine geeignete Normalisierung der Werte. Ein Verschiebung des Wertebereichs
    # reicht dabei aus.
    # Fuer die Kreuzkorrelation koennen Sie die Funktion scipy.signal.correlate2d
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html
    # verwenden. 
    #

    sobel_horizontal = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    sobel_vertical = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    filtered_horizontal = scipy.signal.correlate2d(im_arr, sobel_horizontal, mode="same")
    filtered_vertical = scipy.signal.correlate2d(im_arr, sobel_vertical, mode="same")
    filtered_both = scipy.signal.correlate2d(filtered_horizontal, sobel_vertical, mode="same")
    plt.imshow(filtered_horizontal, cmap=cm.get_cmap('Greys_r'))
    #plt.show()
    plt.imshow(filtered_both, cmap=cm.get_cmap('Greys_r'))
    #plt.show()

    #
    # Berechnen Sie nun die (approx.) Gradienten Magnituden und Orientierungen.
    # Visualisierung der Magnituden: 
    #
    #  - Normalisieren Sie die Werte in das Intervall [0, 1] 

    im_arr = im_arr - np.amin(im_arr)
    im_arr = im_arr / np.amax(im_arr)
    print(im_arr)

    # Visualisierung der Orientierungen. Dabei Verwenden wir den HSV Farbraum
    # http://de.wikipedia.org/wiki/HSV-Farbraum
    #
    # Erlaeutern Sie warum dieser Farbraum dafuer besonders geeignet ist.
    # -> In diesem Farbraum befindet sich der Hellwert, der in einem Intervall von Null bis Eins gemessen werden kann,
    #   das hilft uns, bei den normalisierten Werten
    #
    # - Berechnen Sie die Orientierungen im Bogenmass. Verwenden Sie dabei
    #   numpy.arctan2
    #   http://docs.scipy.org/doc/numpy/reference/generated/numpy.arctan2.html

    orientation = np.arctan2(filtered_horizontal, filtered_vertical)
    magnitude = np.sqrt(np.square(filtered_vertical) + np.square(filtered_horizontal))

    # - Normalisieren Sie die Orientierungen im Bogenmass in das Intervall [0, 1]

    orientation = orientation - np.amin(orientation)
    orientation_normalized = orientation / np.amax(orientation)

    magnitude = magnitude - np.amin(magnitude)
    magnitude_normalized = magnitude / np.amax(magnitude)


    # - Erstellen Sie ein NumPy Array der Form (M,N,3) wobei M die Anzahl Zeilen 
    #   und N die Anzahl Spalten bezeichnet. Setzen Sie alle Werte auf 1. Verwenden
    #   Sie eine float Datentyp.
    #   http://docs.scipy.org/doc/numpy/reference/generated/numpy.ones.html

    tensor = np.ones((im_arr.shape[0], im_arr.shape[1], 3), dtype=float)
    tensor_magnitude = np.ones((im_arr.shape[0], im_arr.shape[1], 3), dtype=float)

    # - Schreiben Sie die normalisierten Orientierungen in den ersten Kanal des 
    #   zuvor erstellen Arrays. Indizieren Sie das Array dazu mit [:,:,0].

    tensor[:, :, 0] = orientation_normalized
    tensor_magnitude[:, :, 0] = magnitude_normalized

    # - Konvertieren Sie das Bild aus dem HSV Farbraum in den RGB Farbraum. Dieser
    #   Farbraum wird standardmaessig in matplotlib verwendet.
    #   http://de.wikipedia.org/wiki/RGB-Farbraum
    #   Verwenden Sie fuer die Konvertierung die Funktion
    #   http://matplotlib.org/api/colors_api.html#matplotlib.colors.hsv_to_rgb

    rgb_tensor = matplotlib.colors.hsv_to_rgb(tensor)
    rgb_tensor_magnitude = matplotlib.colors.hsv_to_rgb(tensor_magnitude)

    # - Visualisieren Sie das RGB Bild
    #

    plt.imshow(rgb_tensor, cmap=cm.get_cmap('Greys_r'))
    plt.show()
    plt.imshow(rgb_tensor_magnitude, cmap=cm.get_cmap('Greys_r'))
    plt.show()
    
    #
    # Erstellen Sie abschliessend eine gemeinsame Visulisierung der Magnituden 
    # und Gradienten. Gehen Sie dabei vor wie bei der Visualisierung der Orientierungen,
    # zusaetzlich schreiben Sie aber noch die normalisierten Magnituden in den V
    # Kanal des HSV Bilds. Fuehren Sie die Konvertierung in den RGB Farbraum durch
    # und visualisieren Sie das Ergebnis.
    #
    # Erlaeutern Sie wie sie den HSV Farbraum fuer die Visualisierung verwendet haben.
    # Erklaeren Sie wie sowohl die Magnituden als auch die Orientierungen an jedem
    # Bildpunkt sichtbar gemacht werden.
    #
    # -----------------------------------
    #
    # Basierend auf den Bildgradienten koennen nun Bilddeskriptoren berechnet werden.
    # Der SIFT Deskriptor basiert auf lokalen Gradientenhistogrammen. Um die Gradienten
    # in einem Histogramm zu erfassen, quantisiert man sie auf 8 Hauptrichtungen.
    #
    # Ein SIFT Deskriptor besteht nun aus 16 Gradientenhistogrammen ueber die 8
    # Hauptrichtungen. Die Gradientenhistogramme werden in 4x4 Zellen berechnet,
    # die um den Mittelpunkt des Deskriptors herum angeordnet sind.
    # Numerisch wird ein SIFT Deskriptor durch einen 128 dimensionalen Vektor 
    # repraesentiert. Dieser ergibt sich indem man die 16 8 Bin Subhistogramme
    # konkateniert.
    # Um SIFT Deskriptoren zu berechnen stehen Bibliotheken wie OpenCV oder vlfeat mit
    # passenden Python Bindings zur Verfuegung
    # Ueblicherweise werden auf dem Dokumentenbild SIFT Deskriptoren
    # in einem regelmaessigen Grid berechnet. Als Parameter werden dabei die 
    # - Aufloesung des Grids (step)
    # - die Deskriptorgroesse eingestellt (size). Die Groesse bezieht sich auf eine Zelle
    #   des Deskriptors. Die Seitenlaenge eines gesamten Deskriptors ergibt sich also
    #   aus cell_size * 4
    # Die Rueckgabe besteht aus den Frames und den Deskriptoren. Die Frames enthalten
    # die x,y Koordinaten jedes einzelnen Deskriptors. desc enthaelt die 128 dimensionalen
    # Vektoren.
    
    # Sie koennen die vorberechneten Deskriptoren aus den beiliegenden pickle Dateien verwenden.
    # '2700270-full*' bezieht sich auf Deskriptoren, die auf dem Bild '2700270.png' berechnet
    # wurden. '2700270-small*' bezieht sich auf die Bilddatei '2700270_small.png'.
    # Die Parameter step_size und cell_size sind wie folgt in den Dateinamen kodiert:
    # 2700270-[full|small]_dense-<step_size>_sift-<cell_size>_descriptors.p
    #
    

    step_size = 15
    cell_size = 3

    pickle_densesift_fn = '2700270-small_dense-%d_sift-%d_descriptors.p' % (step_size, cell_size)
    frames, desc = pickle.load(open(pickle_densesift_fn, 'rb'))

    # 
    # Um eine Bag-of-Features Repraesentation des Bilds zu erstellen, wird ein
    # Visual Vocabulary benoetigt. Im Folgenden wird es in einer Clusteranalyse
    # berechnet. Fuer die Clusteranalyse wird Lloyd's Version des k-means Algorithmus
    # verwendet. Parameter sind
    # - die Anzahl der Centroiden in der Clusteranalyse (n_centroids). Das entspricht 
    # der Groesse des Visual Vocabulary bzw. der Anzahl von Visual Words. 
    # - Der Anzahl von Durchlaeufen des Algorithmus (iter)
    # - Der Initialisierung (minit). Der Wert 'points' fuehrt zu einer zufaelligen
    #   Auswahl von gegebenen Datenpunkten, die als initiale Centroiden verwendet
    #   werden.
    # Die Methode gibt zwei NumPy Arrays zurueck: 
    #  - Das sogenannte Codebuch. Eine zeilenweise organisierte Matrix mit Centroiden (hier nicht verwendet).
    #  - Einen Vektor mit einem Index fuer jeden Deskriptor in desc. Der Index bezieht
    #    sich auf den aehnlichsten Centroiden aus dem Codebuch (labels).
    #
    # Die Abbildung von Deskriptoren auf Centroiden (Visual Words) bezeichnet man als Quantisierung.
    n_centroids = 40 
    _, labels = kmeans2(desc, n_centroids, iter=20, minit='points')
    
    #
    # Die Deskriptoren und deren Quantisierung werden nun visualisiert. Zu jedem 
    # Deskriptor werden dazu die Mittelpunkte und die 4x4 Zellen eingezeichnet.
    # Die Farbe des Mittelpunkts codiert den Index des Visual Words im Visual Vocabulary
    # (Codebuch). Beachten Sie, dass durch diese Kodierung einige Farben sehr 
    # aehnlich sein. 
    # Da das Zeichnen der 4x4 Zellen fuer jeden Deskriptor viel Performance kosten
    # kann, ist es moeglich es ueber das Flag draw_descriptor_cells abzuschalten.
    #
    draw_descriptor_cells = True
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(im_arr, cmap=cm.get_cmap('Greys_r'))
    ax.autoscale(enable=False)
    colormap = cm.get_cmap('jet')
    desc_len = cell_size * 4
    for (x, y), label in zip(frames, labels):
        color = colormap(label / float(n_centroids))
        circle = Circle((x, y), radius=1, fc=color, ec=color, alpha=1)
        rect = Rectangle((x - desc_len / 2, y - desc_len / 2), desc_len, desc_len, alpha=0.08, lw=1)
        ax.add_patch(circle)
        if draw_descriptor_cells:
            for p_factor in [0.25, 0.5, 0.75]:
                offset_dyn = desc_len * (0.5 - p_factor)
                offset_stat = desc_len * 0.5
                line_h = Line2D((x - offset_stat, x + offset_stat), (y - offset_dyn, y - offset_dyn), alpha=0.08, lw=1)
                line_v = Line2D((x - offset_dyn , x - offset_dyn), (y - offset_stat, y + offset_stat), alpha=0.08, lw=1)
                ax.add_line(line_h)
                ax.add_line(line_v)
        ax.add_patch(rect)
    
    plt.show()
    #
    # Varieren Sie die Groesse des Visual Vocabulary sowie die Groesse der Deskriptoren.
    # Diskutieren Sie die Ergebnisse.
    #
    
    # Ueblicherweise arbeiten wir in der Mustererkennung mit einem Datensatz von
    # Trainingsdaten und einem Datesatz von Testdaten. Da der Test die Erkennungs-
    # leistung auf unbekannten Daten simulieren soll, wird das Visuelle Vokabular
    # nur auf den Trainingsdaten berechnet. Um 'unbekannte' Deskriptoren aus dem
    # Testdatensatz zu quantsieren, steht die Methode scipy.cluster.vq.vq zur 
    # Verfuegung.
    #
    #-----------------------------------------------------------------------------------------------------------
    #
    # Bag-of-Features Repraesentation eines Bildes
    # Bisher haben wir die Visual Words bestimmt, die in unserm Bild vorkommen
    # (Variable 'labels'). Berechnen Sie nun die Bag-of-Features 
    # Repraesentation, indem Sie das Histogramm ueber die labels bilden. NumPy
    # bietet dazu die Methode numpy.bincount. Achten Sie dabei unbedingt darauf,
    # dass das Histogramm einen Eintrag fuer jedes Visual Word enthaelt. Default-
    # maessig enthaelt es nur Eintraege fuer die Visual Word Indizes, die in den
    # Eingabedaten vorkommen.
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.bincount.html

    count = np.bincount(labels)

    #
    # Plotten Sie die Bag-of-Features Repraesentation nun.
    # Benuzten Sie dazu einen Bar Plot. Faerben sie die einzelnen Balken entsprechend
    # der oben verwendeten Farbkodierung. Dazu koennen Sie die 'colormap' (siehe oben)
    # wiederverwenden.
    # Zum setzen der Farbe gibt die 'bar' Methode ein Liste mit Objekten zurueck, die
    # sich auf die einzelnen Balken beziehen. Uebergeben Sie diesen Objekten den
    # Farbwert indem Sie 'set_color(color)' aufrufen. 
    #
    x = np.arange(len(count))
    bar_list = plt.bar(x, count)
    for label, bar in enumerate(bar_list):
        color = colormap(label / len(bar_list))
        bar.set_color(color)
    plt.show()
    
    #
    # Llody's Algorithmus zum Clustern von Daten
    # Um eine bessere Vorstellung von Lloyd's Algorithmus zu bekommen soll 
    # dieser nun implementiert und anhand eines 2D Beispiels visualisiert werden.
    # Dazu wird als erstes ein Beispieldatensatz erzeugt:
    
    mean1 = np.array([10, 10])
    cov1 = np.array([[3, .5],
                    [.5, 5]])

    mean2 = np.array([15, 15])
    cov2 = np.array([[5, -.7],
                    [-.7, 3]])
    
    n_samples = 2000
    samples1 = np.random.multivariate_normal(mean1, cov1, n_samples//2)
    samples2 = np.random.multivariate_normal(mean2, cov2, n_samples//2)
    samples = np.vstack((samples1,samples2))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    xx = samples[:, 0]
    yy = samples[:, 1]
    ax.scatter(xx, yy, color='b', marker='o', alpha=1.0)
    ax.set_aspect('equal')
    plt.show()
    
    #
    # Implementieren Sie nun Lloyds Algorithmus 
    # Bestimmen Sie in jeder Iteration den Quantisierungsfehler und brechen Sie
    # das iterative Verfahren ab, wenn der Quantisierungsfehler konvergiert (einen
    # sehr kleinen Schwellwert unterschreitet).
    # Fuer die Implementierung des Algorithmus sind folgende Funktionen hilfreich
    # - scipy.distance.cdist
    # - numpy.mean
    # - numpy.argsort
    # Fuer die Initialisierung waehlen Sie zufaellig Punkte aus der Datenmenge. Dazu
    # kann folgende Funktion hilfreich sein
    # - numpy.permutation 
    #
    # Welche Codebuchgroesse ist fuer die gegebene Verteilung von Daten geeignet?

    def kmeans_lloyd(k):
        clusters = {}
        converged = False
        for i in range(k):
            centroid = tuple(np.random.permutation(samples)[i, :])
            clusters[centroid] = []
        iter = 0
        while iter < 40:
            for sample in samples:
                min_dist = math.inf
                closest_centroid = None
                for center in clusters:
                    dist_centroid_to_sample = np.linalg.norm(np.array(center) - sample.T)
                    if dist_centroid_to_sample < min_dist:
                        min_dist = dist_centroid_to_sample
                        closest_centroid = center
                clusters[closest_centroid].append(sample)

            for centroid in clusters:
                new_centroid = np.array(clusters[centroid]).mean(axis=0)
                clusters[centroid] = clusters.pop(centroid)
                if abs(centroid[0] - new_centroid[0]) < 0.4 and abs(centroid[1] - new_centroid[1]) < 0.4:
                    converged = True
                else:
                    converged = False
            iter += 1
        return clusters

        #
        # Plotten Sie nun das Ergebnis der Clusteranalyse. Faerben Sie dazu die
        # Datenpunkte entsprechend ihrer Clusterzugehoerigkeit.
        # Zeichnen Sie auch die Centroiden mit ein.
        #

    fig = plt.figure()
    ax = fig.add_subplot(111)
    clusters = kmeans_lloyd(3)
    colors = ['r', 'b', 'g']
    for i, centroid in enumerate(clusters):
        xx = []
        yy = []
        for sample in clusters[centroid]:
            x, y = sample
            xx.append(x)
            yy.append(y)
        ax.scatter(xx, yy, color=colors[i], marker='o', alpha=1.0)

    ax.set_aspect('equal')
    plt.show()
    #
    # Variieren Sie nun die Groesse des Codebuchs. Diskutieren Sie Ihre Beobachtungen.
    #
    # Optional:
    # - Visualisieren Sie das Ergebnis der Clusteranalyse nach jeder Iteration.
    # - Experimentieren Sie mit verschiedenen Distanzfunktionen.
    #
    
    plt.close()


#raise NotImplementedError('Implement me')


if __name__ == '__main__':
    aufgabe6()
