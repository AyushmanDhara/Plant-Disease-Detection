# 🌿 PlantGuard - AI Plant Disease Detection System

<p align="center">
  <img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch" alt="PyTorch">
  <img src="https://img.shields.io/badge/Gradio-4.0+-FFB000?style=for-the-badge&logo=gradio" alt="Gradio">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Model-MobileNetV3--Large-orange?style=for-the-badge" alt="Model">
  <img src="https://img.shields.io/badge/Diseases-38+-red?style=for-the-badge" alt="Diseases">
  <img src="https://img.shields.io/badge/Plants-14+-green?style=for-the-badge" alt="Plants">
</p>

> **Protect your plants with cutting-edge AI technology.** Upload a photo of any plant leaf and get instant disease diagnosis with detailed treatment recommendations.

---

## ✨ Features

- 🔬 **AI-Powered Detection**: Uses deep learning (MobileNetV3 Large) for accurate plant disease classification
- 🌿 **Two-Stage Classification**: Validates if the image is a plant leaf before disease detection
- 📊 **38 Disease Classes**: Covers major diseases across 14 different plants
- 💊 **Treatment Recommendations**: Provides organic and chemical treatment options for each disease
- 🎨 **Beautiful UI**: Modern "Biopunk Neon-Nature" themed interface built with Gradio
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔍 **Disease Database**: Searchable database with detailed disease information

---

## 🏥 Supported Plants & Diseases

| Plant | Diseases |
|-------|----------|
| 🍎 Apple | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| 🫐 Blueberry | Healthy |
| 🍒 Cherry | Powdery Mildew, Healthy |
| 🌽 Corn | Cercospora Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| 🍇 Grape | Black Rot, Esca, Leaf Blight, Healthy |
| 🍊 Orange | Huanglongbing (Citrus Greening) |
| 🍑 Peach | Bacterial Spot, Healthy |
| 🫑 Pepper | Bacterial Spot, Healthy |
| 🥔 Potato | Early Blight, Late Blight, Healthy |
| 🫐 Raspberry | Healthy |
| 🌱 Soybean | Healthy |
| 🎃 Squash | Powdery Mildew |
| 🍓 Strawberry | Leaf Scorch, Healthy |
| 🍅 Tomato | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Tomato Yellow Leaf Curl Virus, Tomato Mosaic Virus, Healthy |

---

## 📁 Project Structure

```
Plant_diseases_model/
├── final Gradio project hugging face project files/
│   ├── app.py                    # Main Gradio application
│   ├── model.py                  # PyTorch model definitions
│   ├── disease_data.py           # Disease database
│   ├── Plant_diseases_model1.pth # Trained disease classifier
│   └── leaf_vs_nonleaf_model.pth # Leaf validator model
│
├── model training file/
│   ├── plant_diseases_training_code1.py  # Training script
│   └── leaf_vs_nonleaf_training_file.py  # Leaf validator training
│
├── models/
│   ├── Plant_diseases_model1.pth
│   └── leaf_vs_nonleaf_mobilenetv3.pth
│
├── final html aws project files/
│   └── (Alternative Flask/HTML version)
│
└── README.md                     # This file
```

---

## 🧠 Model Architecture

### Disease Classifier
- **Architecture**: MobileNetV3 Large
- **Input Size**: 224×224 pixels
- **Training Data**: New Plant Diseases Dataset (Augmented)
- **Classes**: 38 (disease + healthy)

### Leaf Validator
- **Architecture**: MobileNetV3 Large
- **Purpose**: Two-stage classification - validates if image is a plant leaf
- **Classes**: 2 (Leaf, Non-Leaf)

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **PyTorch** | Deep learning framework |
| **TorchVision** | Image transforms and pre-trained models |
| **Gradio** | Web UI framework |
| **MobileNetV3** | Lightweight CNN architecture |
| **Pillow** | Image processing |
| **NumPy** | Numerical computing |

---

## 📸 How It Works

1. **Upload**: User uploads a photo of a plant leaf
2. **Validation**: The leaf validator checks if the image contains a plant leaf
3. **Detection**: If valid, the disease classifier identifies the disease
4. **Results**: Detailed diagnosis with:
   - Disease name and severity
   - Symptoms
   - Causes
   - Organic treatment options
   - Chemical treatment options
   - Prevention tips

---

## 🎯 Usage Tips

For best results:
- Take clear, well-lit photos
- Focus on the affected area
- Capture multiple angles if possible
- Check both sides of leaves

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [New Plant Diseases Dataset](https://www.kaggle.com/) - Training data
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Gradio](https://gradio.app/) - UI framework
- [MobileNetV3](https://arxiv.org/abs/1905.02244) - Model architecture

---

<p align="center">
  Made with ❤️ for plant health
</p>


