import io
import base64
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template, url_for, request, redirect

# application
app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")


# check if user inputs are correct
@app.route("/valid", methods=["POST", "GET"])
def valid():
    if request.method == "POST":
        pair = request.form["pair"].upper()
        days = request.form["days"]
        # if they are send them to data function to calculate and print the prediction
        if (pair == 'BTC' or pair == 'ETH' or pair == 'BNB' or pair == 'XRP' or pair == 'ADA') and (10 <= int(days) <= 730):
            return redirect(url_for("data", pair=pair, days=days))
        # if not ask user to use new inputs
        else:
            if not(pair == 'BTC' or pair == 'ETH' or pair == 'BNB' or pair == 'XRP' or pair == 'ADA') and (10 <= int(days) <= 730):
                invalidpair = True
                invaliddays = False
            elif (pair == 'BTC' or pair == 'ETH' or pair == 'BNB' or pair == 'XRP' or pair == 'ADA') and not(10 <= int(days) <= 730):
                invalidpair = False
                invaliddays = True
            else:
                invalidpair = True
                invaliddays = True

            return render_template("index.html", invalidpair=invalidpair, invaliddays=invaliddays)
    else:
        return render_template("index.html")


# get pair and days user inputs from html page
@app.route("/data/<pair>-<days>", methods=["POST", "GET"])
def data(pair, days):
    coin_data = yf.download(pair + "-USD", period=days + "d", interval="1d")['Close']

    # create array in size of days given
    amount = []
    for i in range(int(days)):
        amount.append(i)

    # check how many data user wants and take accordingly a number of degree for the polynomial
    cond = int(days)
    if 10 <= cond <= 50:
        degree = 10
    elif 50 < cond <= 100:
        degree = 15
    elif 100 < cond <= 200:
        degree = 20
    elif 200 < cond <= 400:
        degree = 25
    else:
        degree = 30

    # create the polynomial from the data gathered
    model = numpy.poly1d(numpy.polyfit(amount, coin_data, degree))
    line = numpy.linspace(amount[0], amount[-1], int(coin_data[-1]))

    # chart for close price data on the pair user chose and save it
    plt.figure(1)
    plt.scatter(amount, coin_data, color="red")
    plt.plot(line, model(line), color="black")
    fig = plt.gcf()

    # Convert chart to PNG image
    pngImage_1 = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage_1)

    # Encode PNG image to base64 string
    pngImageB64String_1 = "data:image/png;base64,"
    pngImageB64String_1 += base64.b64encode(pngImage_1.getvalue()).decode('utf8')
    fig.clf()

    # bar chart close price data on the pair user chose and save it
    plt.figure(2)
    plt.bar(amount, coin_data, color="red")

    # clear graph (incase user recalls the function)
    fig = plt.gcf()

    # Convert chart to PNG image
    pngImage_2 = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage_2)

    # Encode PNG image to base64 string
    pngImageB64String_2 = "data:image/png;base64,"
    pngImageB64String_2 += base64.b64encode(pngImage_2.getvalue()).decode('utf8')

    # clear column graph (incase user recalls the function)
    fig.clf()

    # predict and print future price
    prediction = model(amount[-1] + 1)

    # convert data to html format
    data_ = pd.DataFrame(coin_data)
    # remove time from date
    data_.index = data_.index.tz_localize(None)
    return render_template("index.html", prediction=prediction, url1=pngImageB64String_1, url2=pngImageB64String_2, data=[data_.to_html(classes='data')])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
