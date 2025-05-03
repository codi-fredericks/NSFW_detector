#https://cdn.discordapp.com/attachments/1368034531579269124/1368034575309344838/f_002d6d.png?ex=6816c0fb&is=68156f7b&hm=920b2368cb5926e10e83ec44435b961794567715f01daca8eb2e6b1e8372e6d5&
import requests
from PIL import Image,  ImageSequence
from io import BytesIO
import tempfile
from nudenet import NudeDetector
import os


async def detect_from_url(url, lookfor=None):
    if lookfor is None:
        lookfor = [
    "FEMALE_GENITALIA_COVERED",
    "FACE_FEMALE",
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "BELLY_COVERED",
    "FEET_COVERED",
    "ARMPITS_COVERED",
    "ARMPITS_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
    "FEMALE_BREAST_COVERED",
    "BUTTOCKS_COVERED",
]
# Step 1: Load image from URL
    response = requests.get(url)
    if response.ok:
        img = Image.open(BytesIO(response.content))

        # Step 2: Initialize classifier
        classifier = NudeDetector()
        results = []

        # Step 3: Handle static vs animated
        if getattr(img, "is_animated", False):
            frames = ImageSequence.Iterator(img)
        else:
            frames = [img]

        # Step 4: Iterate through frames
        for i, frame in enumerate(frames):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                frame.convert("RGB").save(temp_file.name)
                temp_path = temp_file.name

            # Classify the frame
            result = classifier.detect(temp_path)
            results.append((i, result))

            # Cleanup
            os.remove(temp_path)

            # Check for matches
            for item in result:
                if item['class'] in lookfor:
                    return result  # early return if match found
    return False  # no match found

if __name__ == '__main__':
    labels = [

        "BUTTOCKS_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_BREAST_EXPOSED",
        "ANUS_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
    ]
    urls = [
        "https://cdn.discordapp.com/attachments/1049604981923254342/1365870455046541323/images8.jpg?ex=681621bd&is=6814d03d&hm=4691b229a8ea569d3c3a222155ebbb7ceb752102685f03ad7926d98e073f2315&",
        "https://cdn.discordapp.com/attachments/1049604981923254342/1365494300049277049/Screenshot_2025-04-06_213654.png?ex=6816bdaa&is=68156c2a&hm=cf990146d87e185566af5e00221f97b08323ac8bd5f068fb4ec2a58823c076a5&",
        "https://cdn.discordapp.com/attachments/1049604981923254342/1363313397663531028/ntg53wjl.gif?ex=6816b78b&is=6815660b&hm=5a62489661c8609716dd0724061331ef215bdd8e2f513d4f22fdc08994355b53&",
        "https://cdn.discordapp.com/attachments/1013740145389867039/1362900945956114602/Screenshot_20250418_143908_Steam2.jpg?ex=681688ea&is=6815376a&hm=18787a3d222e4e38031200824df9987606e4cf01c68656046b060fbf274630c1&",
        "https://cdn.discordapp.com/attachments/1013740145389867040/1360355505167667370/Juno_Overwatch.png?ex=681680ca&is=68152f4a&hm=2483f0b4150631f0a29d2b5ae90731f1e1aa66f593df6b2c3c5c49771a05abb4&",
        "https://cdn.discordapp.com/attachments/1013740145389867040/1360354462190800926/blo.jpg?ex=68167fd1&is=68152e51&hm=5f72c730d814eda10a4a518cbc9723f8a69ec155789176e2a22ad188c5025b98&",
        "https://imagex1.sx.cdn.live/images/pinporn/2019/03/27/20893884.gif?width=300",
        "https://cdn.discordapp.com/attachments/1368034531579269124/1368034575309344838/f_002d6d.png?ex=6816c0fb&is=68156f7b&hm=920b2368cb5926e10e83ec44435b961794567715f01daca8eb2e6b1e8372e6d5&",
        "https://i.pinimg.com/736x/a2/ae/5c/a2ae5c69b13a66014fefe2a6c9be9797.jpg",
        "https://i.pinimg.com/736x/51/2b/e4/512be435a72ad8016ec1f8daf8ac6cd1.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJwcvczIiqRTkAxCBbYPesN5y_-54j8Mfro92daky96C9l87g1HzgGAIk&s=10",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMOWkVDCoLcVlYuUtLLw-EbSUfz8JylPLjYnvPrnXcQVbYz93v_sIq0F0&s=10"
    ]
    for url in urls:
        print("/n/n==================================================")
        print(detect_from_url(url, labels))
        print("==================================================")
