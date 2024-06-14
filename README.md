# Réseaux
Projet Programmation Licence Informatique 3eme année
VISUALISATEUR DE TRAFIC RÉSEAU

Par : BABANAZAROVA Dilyara 28709428
	  CELIK Simay 28713301
	  Groupe 4

Dans ce projet on a codé un visualisateur des flux de trafic réseau. Notre programme prend un fichier texte qui contient hexdump ou hexdump+asciidump où il y a plusieurs trames. Il commence d'abord à séparer ces trames et les décoder. Il sépare chaque trame par couche ou plus précisément, par les protocoles Ethernet, IP, TCP. Prenant les informations nécessaires de ces protocoles comme : les adresses IP, le type, les numéros de port, le numéro de séquence, le numéro d'acquittement, les drapeaux et la valeur de champs Window, on crée les objets de chaque couche et les enregistre dans un flux. En utilisant ce flux on crée après un fichier texte sorti et y affiche chronologiquement les trames lues. Ainsi, une interface graphique va apparaître automatiquement et afficher la chronologie en distinguent les connections par les couleurs différentes. Dans l'interface graphique, on a aussi un petit champ pour filtrer les connexions. Il faut taper les filtres sur l'entrée et cliquer sur le bouton "Filter". On peut les filtrer par les adresses IP client, par les adresses IP serveur et aussi par les types protocoles (HTTP et TCP). Juste a cote de la touche "Filter" on trouve la touche "Reset". En l'appuyant on revient a l'état initial de l'affichage.

De plus, notre programme détecte les exceptions et les signale sur le terminal. Il gère aussi ces connexions selon les cas : soit le code les ignore et continue à exécuter, soit il se termine. Dans notre code on vérifie les cas :
	1. Le fichier source est vide
	2. Le fichier de mauvais format
	3. Le fichier source est trop grand/Dépassement du nombre de trames autorisé
	4. Les trames avec les protocoles inconnus
	5. Les fichiers contenant de/des trames incomplets.

Le code plus détaillé :

###########################################################
######################### LES CLASSES #####################
###########################################################

Pour programmer ce visualisateur on a créé 3 classes pour différencier les protocoles Ethernet, IP , TCP et aussi  on a les classes Trame et Flux.
 
	Classe TCP :
		La classe a 9 attributs : portSrc, portDst, seq, ack, len, win, flags, msg, HTTP. 
		
		Les fonctions :
			1. __init__ -> qui prend en paramètre toutes les valeurs et les initialise sauf HTTP qui vaut False au début.

			2. findServer(self) -> renvoie 0 si serveur est la source et 1 si serveur est le client.
	
			3. isThereHTTP(self) -> renvoie un boolean si tcp encapsule un HTTP.

			4. printFlags(un segment) -> qui envoie une chaîne de caractère avec les drapeaux de ce segment en vérifiant le champ flags.

			5.toStringTCP(un segment) -> qui affiche les champs de l’entête TCP s’il n y pas de HTTP encapsulé sinon affiche le msg HTTP.


	Classe IP : 
		Cette classe aussi a 5 attributs : dest : @ipdest, src : @ipsrc, len, protocol et tcp de type TCP. 

		Ses fonctions : 
			1. __init__(self,adst,asrc,len,protocol,tcp : TCP) -> qui initialise ses attributs.

			2. printIP(self)

			3. findServer(self) -> si le serveur est la source alors la fonction renvoie l'@ IP src contenu dans le paquet IP et l'@ dest sinon.

			4. findClient(self) -> si le client est la source alors la fonction renvoie l'@ IP src contenu dans le paquet IP et l'@ dest sinon.

			5. findClientPort(self) -> renvoie le port du client.

			6. toStringIP(self) -> qui affiche le paquet IP encapsulé dans cette trame.
	
	
	Classe Ethernet :
		Elle a 5 attributs : 
			1. macDst - l'@ MAC de destination
			2. macSrc - l'@ MAC de source
			3. type - pour savoir le type de protocole encapsulé.
			4. len - pour la taille de l'entête d'Ethernet
			5. ip - protocole IP.
		
		Ses fonctions :
			1. __init__(self,md,ms,type,ip : IP) -> qui initialise ses attributs. 

			2. toStringEth(self) -> qui affiche le paquet IP encapsulé dans cette trame.
				

	Classe Trame :
		Elle a 5 attributs : eth de type Ethernet, ipServer, ipClient qui sont les variables pour les adresses IP du client et serveur. 

		Ses fonctions :
			1. __init__(self, eth : Ethernet) -> qui initialise ses attributs. Et pour initialiser les addresses ipServer et ipClient elle utilise la fonction findClientServeur().

			2. findClientServeur(self) -> qui trouve les valeurs des attributs ipServer et ipClient et les initialise :
				1. Si le portSource de tcp égale à 80, alors ipServer= IP.source et ipClient=IP.dest
				2. Sinon, les valeurs sont inversées.
			
			3. printTrame(self) -> qui affiche les valeurs importantes d'une trame. On affiche aussi les flèches pour savoir de quelle machine à laquelle est envoyé la trame.  


	Classe Flux : 
		Cette classe prend une liste des trames comme un attribut.
		
		Les fonctions :
	
			1. __init__(self, listTrames : Trame) -> initialise la liste des trames.

			2. writeSortie(self) -> retourne la sortie des trames en utilisant la fonction printTrames(self).

			3. printTrames(self)


############################################################
##################### FONCTIONS DU PROGRAMME ###############
############################################################
On a 4 fonctions primaires pour lire les trames, pour les decoder, filtrer, les engresitrer dans un fichier texte. On a aussi une petite main ou on prend d'abord le nom du fichier à tester, on crée une interface graphique et on lance le programme. 

1. readFile(filename) -> retourne une liste des trames en lisant d’un fichier contenant plusieurs trames.

2. tramReader(trame) -> décode la trame selon les champs des entetes et cree les objets des protocoles Ethernet, IP, TCP et HTTP (s'il y en a) avec les valeurs trouve et retourne une Trame crée avec ces protocoles.

3. createFile(filename) -> cree et retourne le fichier sorti en utilisant les fonctions writeSortie(), readFile(),tramReader(). 

4. hextoRGB(la couleur en hexa) -> convertit la couleur en format hexa en format RGB. 

5. colorsAreClose(new, prev) -> rend un booléen. Elle s'empêche d'avoir 2 couleurs qui sont proche l'un de l'autre.

6. randomColor(nombre) -> retourne une liste de nombre couleurs différentes qui sont générés aléatoirement. On va utiliser ces couleurs pour l'affichage des différentes connections dans le visualisateur.

#############################################################
############################ MAIN ###########################
#############################################################

7. On cree notre interface avec la librairie Tkinter de Python. Pour distinguer les connexions differentes, on a un dictionnaire qui lit les trames et cree un élément avec la clé (@ipClient, @ipServeur, portClient, portServeur) et la valeur est un entier=le numéro de connexion et aussi on a une liste des couleurs pour chaque connexion différente. Pour chaque trame on regarde si on a déjà cette connexion. Si ce le cas, on prend la valeur de ce couple qui est l'indice de la liste des couleurs. Sinon on cree un nouvel élément de dictionnaire et la valeur sera la prochaine couleur. 


	1. affichageLabel(couple,protoLigne,l) -> on cree dans cette fonction les connexions avec les types de la librairie Tkinter qu'on va afficher dans l'interface. 

	2. filtering() -> dans cette fonction on filtre les connexions lues du fichier selon les types protocoles et selon les adresses IP client-serveur.
	Si on veut filtrer par 
		1. l'@ IP :
			On doit écrire "ipc=="+ipClient ou "ips=="+ipServeur
		2. le type protocole :
			On doit écrire "HTTP", "TCP", "http" ou bien "tcp"

	3. reset() -> on met à jour l'affichage de l'interface graphique avec le nouveau résultat du filtrage.
	

