from lib.auth import FirebaseApp
import generated.misc_pb2 as misc_pb2
import generated.config_pb2 as config_pb2
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/diploma/dating-diploma/conf/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"


config = config_pb2.TAuthConfig(Enabled=False)
app = FirebaseApp(config)
token="dwgUy5nJT5SAM71AgVYWjn:APA91bGDzTSYU9JCI2-AkCu8BoYFzFxMM-F9rPJeDPhZNp8jNFV1zoLsho4ZhoDDzZ0N3CezkvZw7K1UdPjgBDqoskvTYJ0KE35ZpLGuE2JZ0g2oNjCIGa4WQ1YDlRLzKCnvdAcW4fGV"
app.send_user_push(token, "Привет", "Я пуш уведомление")


