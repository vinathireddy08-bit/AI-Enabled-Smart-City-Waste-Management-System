import pickle
import os



model_path = os.path.join(
    os.path.dirname(__file__),
    "waste_prediction_model.pkl"
)



with open(model_path,"rb") as file:

    model = pickle.load(file)




def predict_fill_level(current_fill):


    prediction = model.predict(
        [[current_fill]]
    )


    return round(prediction[0],2)



if __name__ == "__main__":


    result = predict_fill_level(70)


    print(
        "Predicted Fill Level:",
        result,
        "%"
    )