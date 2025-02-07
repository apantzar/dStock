import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

print("🄳🅂🅃🄾🄲🄺...")

# Loading data
ans = True
while ans:
    print(
        """
=========[Menu]=========
    a. META (Facebook)
    b. APPLE
    c. TESLA
    d. Exit/Quit
========================
    """
    )
    ans = input("Select a company to predict: ")
    if ans == "a":
        company = "META"
        break
    elif ans == "b":
        company = "AAPL"
        break
    elif ans == "c":
        company = "TSLA"
        break
    elif ans == "d":
        print("\n Goodbye")
        exit(-1)
    else:
        print("\n Not Valid Choice Try again")

start = dt.datetime(2012, 1, 1)
end = dt.datetime(2024, 12, 1)

data = yf.download(company, start=start, end=end)

# Prepare Data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data["Close"].values.reshape(-1, 1))

prediction_days = 100

x_train = []
y_train = []

for x in range(prediction_days, len(scaled_data)):
    x_train.append(scaled_data[x - prediction_days : x, 0])
    y_train.append(scaled_data[x, 0])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# Model

model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50))
model.add(Dropout(0.2))

model.add(Dense(units=1))
model.compile(optimizer="adam", loss="mean_squared_error")
model.fit(x_train, y_train, epochs=25, batch_size=32)

"""Testing -> Test model on existing data"""

# Load

test_start = dt.datetime(2020, 1, 1)
test_end = dt.datetime.now()

# ✅ FIXED: Use yfinance instead of pandas_datareader
test_data = yf.download(company, start=test_start, end=test_end)
actual_prices = test_data["Close"].values

total_dataset = pd.concat((data["Close"], test_data["Close"]), axis=0)
model_inputs = total_dataset[
    len(total_dataset) - len(test_data) - prediction_days :
].values

model_inputs = model_inputs.reshape(-1, 1)
model_inputs = scaler.transform(model_inputs)

# Test Data

x_test = []
for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x - prediction_days : x, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

predicted_prices = model.predict(x_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

# Plotting test

plt.plot(actual_prices, color="blue", label=f"Actual Price")
plt.plot(predicted_prices, color="green", label=f"Predicted Price")
plt.title(f"{company} Price [OLD]")
plt.xlabel("Time")
plt.ylabel("Stock")
plt.legend()
plt.show()

# Predict Next

real_data = [
    model_inputs[len(model_inputs) + 90 - prediction_days : len(model_inputs + 90), 0]
]
real_data = np.array(real_data)
real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

prediction = model.predict(real_data)
prediction = scaler.inverse_transform(prediction)
print(f"\n\nThree months price prediction: {prediction}")
