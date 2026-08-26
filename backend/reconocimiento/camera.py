import cv2

MODEL_PATH = "face_detection_yunet_2023mar.onnx" #Es una red neuronal ligera
#para la deteccion de rostros

cap = cv2.VideoCapture(0) #inicia la captura desde la camara 0

if not cap.isOpened():
    print("Error en la camara")
    exit() #Comprueba si la camara no se logro abrir y si se cumple sale error

ret, frame = cap.read() # lee el fotograma inicial, ret es un boolean
#y frame contiene una matriz si resulta ser false no hara nada


if not ret:
    print("No se logro leer el primer frame")
    exit() #Comprueba si hubo un error en el frame

h, w = frame.shape[:2] #Extrae la altura (h) y el ancho (w) en pixeles del fotograma inicial

detector = cv2.FaceDetectorYN.create( #Crea e inicializa el objeto detector YuNet con la configuracion
    MODEL_PATH, #ruta
    "", # configuracion de red
    (w, h), # tamaño y ancho
    score_threshold=0.6, #umbral de confianza
    nms_threshold=0.3, #umbral nms: elimina cuadros superpuestos sobre el mismo
    top_k=5000 #numero maximo de caras
)

while True: #inicia un bucle infinito para procesar el video en tiempo real
    ret, frame = cap.read()

    if not ret: #Si la captura falla muestra el mensaje y sale del ciclo
        print("No se logro leer el frame, saliendo")
        break

    detector.setInputSize((frame.shape[1], frame.shape[0])) #se ejecuta la deteccion facil en el fotograma
    #'-' ignora el valor de retorno secundario y faces guarda los valores

    _, faces = detector.detect(frame)

    if faces is not None: 
        for face in faces:
            x, y, w_box, h_box = face[:4].astype(int)
            score = face[-1]

            cv2.rectangle(
                frame,
                (x, y),
                (x + w_box, y + h_box),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{score:.2f}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

    cv2.imshow("camara funcionando correctamente", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()