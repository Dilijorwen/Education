import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image


st.set_page_config(
    page_title="Человек или Лошадь",
    layout="centered"
)

st.title("Человек или Лошадь")
st.write("Загрузите фотографию и модель предскажет, кто изображен на фото **человек** или a **лошадь**.")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@st.cache_resource
def load_model():
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 1)
    model.load_state_dict(torch.load("horse_human_resnet18.pth", map_location=device))
    model.to(device)
    model.eval()
    return model

model = load_model()

transform = transforms.Compose([
    transforms.Resize(148),
    transforms.CenterCrop(128),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

uploaded_file = st.file_uploader(
    "Выберите фото",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Загруженное изображение")

    x = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logit = model(x)
        prob = torch.sigmoid(logit).item()

    st.subheader("Предсказание")

    label = "Человек 🧑" if prob >= 0.5 else "Лошадь 🐎"
    st.markdown(f"### Результат: **{label}**")
    st.write(f"**Вероятность что это человек равна:** `{prob * 100:.0f}%`")