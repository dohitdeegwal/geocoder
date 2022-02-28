from flask import Flask, redirect, render_template, request, make_response
import pandas as pd
from geopy.geocoders import ArcGIS

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/success", methods=["POST", "GET"])
def success():
    global file, df
    if request.method == "POST":
        file = request.files["file"]
        try:
            df = pd.read_csv(file)
            address_col_name = "not found"
            columns = tuple(df.columns)
            cases = ("address", "Address", "ADDRESS")

            for case in cases:
                if case in columns:
                    address_col_name = case
                    break

            if address_col_name == "not found":
                return render_template("index.html", text="File does not contain an address column", classType="text-warning")

            addresses = list(df[address_col_name])
            global nom
            nom = ArcGIS()

            coordinates = [nom.geocode(address) for address in addresses]
            latitudes = [
                coordinate.latitude if coordinate is not None else None for coordinate in coordinates]
            longitudes = [
                coordinate.longitude if coordinate is not None else None for coordinate in coordinates]

            df["Latitude"] = latitudes
            df["Longitude"] = longitudes

            result = df.to_html(
                classes="table table-bordered table-hover w-auto", index=False)
            return render_template("index.html", table=result, btn="download_btn.html")

        except UnicodeDecodeError:
            return render_template("index.html", text="Please upload a CSV file.", classType="text-danger")
        except pd.errors.EmptyDataError:
            return render_template("index.html", text="File empty", classType="text-danger")
    else:
        return redirect("/")


@app.route("/download")
def download():
    global df
    response = make_response(df.to_csv(index=False))
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)
