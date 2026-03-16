import torch
from torchvision import datasets, transforms

# 1. The Translation Layer for Images
# This function intercepts a raw image and mathematically converts it into a PyTorch Tensor
tensor_transform = transforms.ToTensor()

# 2. Download the Training Data
print("Downloading FashionMNIST Training Data...")
train_data = datasets.FashionMNIST(
    root="data", # This will create a 'data' folder in your directory
    train=True,  # We want the training set (the 80%)
    download=True,
    transform=tensor_transform
)
print("Download Complete!")

# 3. Inspecting the Matrix
# Let's pull the very first image and its label out of the dataset
first_image, first_label = train_data[0]

# 4. Prove the dimensions
# print(f"Mathematical Shape of Image: {first_image.shape}")
# print(f"Raw Label (The Answer): {first_label}")


from torch.utils.data import DataLoader

# 5. The Batching Engine
# We tell the engine to grab 64 images at a time, and shuffle them so the AI doesn't memorize the order.
print("Initializing DataLoader...")
train_loader = DataLoader(dataset=train_data, batch_size=64, shuffle=True)
print("DataLoader Ready!")

# 6. Prove the Batch Shape
# We extract exactly one batch from the engine to inspect it
train_features_batch, train_labels_batch = next(iter(train_loader))

# print(f"Batch Features Shape: {train_features_batch.shape}")
# print(f"Batch Labels Shape: {train_labels_batch.shape}")

from torch import nn

# 7. Architecting the Brain
class VisionBrain(nn.Module):
    def __init__(self):
        super().__init__()
        # Step A: Flatten the 2D image (28x28) into a 1D vector (784)
        self.flatten = nn.Flatten()
        
        # Step B: The Hidden Layers (The Neurons)
        # We connect 784 inputs to 512 internal neurons, apply ReLU, then output to 10 classes
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(in_features=28*28, out_features=512),
            nn.ReLU(), # The activation function (allows the AI to learn complex, non-linear patterns)
            nn.Linear(in_features=512, out_features=10) # 10 final outputs for 10 clothing types
        )

    def forward(self, x):
        # Step C: The Wiring (How data moves)
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

# 8. Instantiate the Brain
print("Building the Neural Network...")
model = VisionBrain()
print("Network Built Successfully!")

# 9. The Untrained Test
# Let's pass our batch of 64 images directly into the raw, completely untrained brain
raw_predictions = model(train_features_batch)
# print(f"Prediction Matrix Shape: {raw_predictions.shape}")

# 10. Initialize the Judge and the Mechanic
loss_fn = nn.CrossEntropyLoss()
# We hand the Optimizer the model's internal weights (parameters) so it knows what to tweak. 
# lr=0.01 is the "Learning Rate" (how aggressively it changes the math).
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

# 11. The Training Engine
epochs = 10 # An Epoch is one full sweep through all 60,000 images
print("Starting Training Engine...")

for epoch in range(epochs):
    print(f"Epoch {epoch+1}\n-------------------------------")
    
    # Loop through the DataLoader (grabbing 64 images at a time)
    for batch_number, (images, labels) in enumerate(train_loader):
        
        # Step A: Forward Pass (Make a guess)
        predictions = model(images)
        
        # Step B: Calculate the Error (How wrong was the guess?)
        loss = loss_fn(predictions, labels)
        
        # Step C: Backpropagation (The Learning)
        optimizer.zero_grad() # Clear the mechanic's old memory
        loss.backward()       # Calculate the exact mathematical tweaks needed
        optimizer.step()      # Apply the tweaks to the neurons
        
        # Print a status report every 100 batches so we can watch it learn
        if batch_number % 100 == 0:
            current_loss = loss.item()
            # This prints the current error margin, and how many images we have processed
            print(f"Loss: {current_loss:>7f}  [{batch_number * len(images):>5d}/60000]")

print("Training Complete!")

# 12. Load the Hidden Test Data
print("\nDownloading FashionMNIST Test Data...")
test_data = datasets.FashionMNIST(
    root="data",
    train=False, # We want the hidden 10,000 testing images
    download=True,
    transform=tensor_transform
)
test_loader = DataLoader(dataset=test_data, batch_size=64, shuffle=False)

# 13. The Testing Engine
# Lock the model's weights so it cannot learn during the exam
model.eval()

correct_predictions = 0
total_images = len(test_loader.dataset)

# Turn off the gradient engine to save memory and prevent cheating
with torch.no_grad():
    for images, labels in test_loader:
        # Forward pass (The AI takes the exam)
        predictions = model(images)
        
        # Calculate exactly how many it guessed correctly in this batch
        # .argmax(1) finds the index of the highest confidence score (0-9)
        correct_predictions += (predictions.argmax(1) == labels).type(torch.float).sum().item()

# 14. The Final Grade
accuracy = (correct_predictions / total_images) * 100
print(f"Final Blind Test Accuracy: {accuracy:>0.1f}%")


# 15. The Real-World Translation Layer
# This dictionary maps the AI's math (0-9) back to English
fashion_dictionary = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

# 16. Pull a single image from the hidden test vault
model.eval()
# We grab the very first image (index 0) and its true label
image_tensor, true_label_index = test_data[0] 

# 17. Ask the AI to predict
with torch.no_grad():
    # Pass the image tensor into the brain
    prediction_logits = model(image_tensor)
    
    # Find the index of the highest confidence score
    predicted_index = prediction_logits[0].argmax(0).item()
    
    # Translate the indexes back to English words
    predicted_clothing = fashion_dictionary[predicted_index]
    actual_clothing = fashion_dictionary[true_label_index]
    
    print("\n--- INFERENCE TEST ---")
    print(f'AI Predicted: "{predicted_clothing}"')
    print(f'Actual Answer: "{actual_clothing}"')


# 18. The Production Bridge (Serialization)
print("\nSaving Model Weights for Production...")

# We extract the learned math (state_dict) and save it as a .pth file
torch.save(model.state_dict(), "vision_weights.pth")

print("Model successfully frozen as 'vision_weights.pth'!")    