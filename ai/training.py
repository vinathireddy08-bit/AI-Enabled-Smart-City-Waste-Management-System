import pickle
import numpy as np
from sklearn.linear_model import LinearRegression


# Training data
# Current fill level → Future fill level

X = np.array([
    [20],
    [30],
    [40],
    [50],
    [60],
    [70],
    [80]
])


y = np.array([
    30,
    45,
    55,
    65,
    75,
    90,
    100
])


# Create model

model = LinearRegression()


# Train model

model.fit(X, y)



# Save model

with open("waste_prediction_model.pkl","wb") as file:

    pickle.dump(model,file)



print("AI Model Training Completed")