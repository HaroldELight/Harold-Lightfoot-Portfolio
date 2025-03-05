# %%
# steps to train a model on the MNIST dataset
# 1. load the dataset
# 2. Look at the dataset
# 3. Prepare the dataset
# 4. Build the model
# 5. Train the model
# 6. Evaluate the model
# 7. Save the model

# %% [markdown]
# # 1. Load the dataset

# %%
# Imports
import numpy as np
import pandas as pd

# %%
# Variables
train_images = np.fromfile('train-images.idx3-ubyte', dtype=np.uint8)
train_labels = np.fromfile('train-labels.idx1-ubyte', dtype=np.uint8)
test_images = np.fromfile('t10k-images.idx3-ubyte', dtype=np.uint8)
test_labels = np.fromfile('t10k-labels.idx1-ubyte', dtype=np.uint8)
print(train_images.shape)
print(train_labels.shape)
print(test_images.shape)
print(test_labels.shape)



# %%
# Imports
import matplotlib.pyplot as plt

# %%
train_images

# %% [markdown]
# # 2. Prepare the dataset

# %%
# Remove the header
train_images = train_images[16:].reshape(60000, 28, 28)
test_images = test_images[16:].reshape(10000, 28, 28)
train_labels = train_labels[8:].reshape(60000)
test_labels = test_labels[8:].reshape(10000)

# %% [markdown]
# # 3. Look at the dataset

# %%
# Imports
import matplotlib.pyplot as plt

# %%
# Plot the first 10 images with their labels
for i in range(10):
    img = train_images[i]
    label = train_labels[i]
    plt.subplot(2, 5, i+1)
    plt.imshow(img, cmap='gray')
    plt.title(label)
    plt.xticks([])
    plt.yticks([])
plt.show()

# %% [markdown]
# # 4. Build the model

# %%
# Imports
from sklearn.linear_model import LogisticRegression

# %%
train_images.shape

# %%
# Label the variables
X_train = train_images.reshape(60000, 784)
X_test = test_images.reshape(10000, 784)
y_train = train_labels
y_test = test_labels

# %% [markdown]
# # 5. Train the model

# %%
clf = LogisticRegression()
clf.fit(X_train, y_train)

# %% [markdown]
# # 6. Evaluate the model

# %%
# imports
from sklearn.metrics import accuracy_score

# %%
# make predictions
y_pred = clf.predict(X_test)

# %%
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# %%
# 1st model score
print("First model score with default parameters:", accuracy)

# %% [markdown]
# # Big Success


