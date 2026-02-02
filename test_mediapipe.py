#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## test
##

import cv2
import mediapipe as mp
import os
import time

def test_mediapipe_mesh():
    
    print("--- LOCKSENSE: SMART SECURITY ACTIVE ---")
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

    # --- PARAMÈTRES LOCKSENSE ---
    GRACE_PERIOD = 5  # secondes avant verrouillage
    last_seen_time = time.time()
    is_locked = False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access webcam.")
        return

    with mp_face_mesh.FaceMesh(
            static_image_mode = False,
            max_num_faces = 1,
            refine_landmarks = True,
            min_detection_confidence=0.5) as face_mesh:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            current_time = time.time()

            if results.multi_face_landmarks:
                # VISAGE DÉTECTÉ : On réinitialise le timer
                last_seen_time = current_time
                status_text = "USER PROTECTED"
                color = (0, 255, 0)
                
                # Dessiner le mesh pour le débug
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=drawing_spec)
            else:
                # VISAGE ABSENT : calcul depuis combien de temps
                absence_duration = current_time - last_seen_time
                remaining_time = max(0, int(GRACE_PERIOD - absence_duration))
                
                status_text = f"USER AWAY - LOCKING IN {remaining_time}s"
                color = (0, 0, 255)

                # DÉCLENCHEMENT DU VERROUILLAGE
                if absence_duration >= GRACE_PERIOD and not is_locked:
                    print("LockSense: Triggering lock...")
                    os.system("xdg-screensaver lock")
                    is_locked = True # Évite de lancer la commande en boucle
                    # Optionnel : break si on veut arrêter le script après verrouillage

            # Affichage des infos sur l'écran
            cv2.putText(frame, status_text, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            cv2.imshow('LockSense - Security Monitor', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("--- LOCKSENSE: PROGRAM EXIT ---")

if __name__ == "__main__":
    test_mediapipe_mesh()
