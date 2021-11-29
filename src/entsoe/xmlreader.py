from lxml import objectify
import isodate


def day_ahead_price_list(xml):
    root = objectify.fromstring(xml)

    ts = root.TimeSeries
    period = ts.Period
    start_time = isodate.parse_datetime(period.timeInterval.start.text)
    end_time = isodate.parse_datetime(period.timeInterval.end.text)
    duration = isodate.parse_duration(period.resolution.text)

    data = {
        "type": root.type.text,
        "area": ts["in_Domain.mRID"].text,
        "currency": ts["currency_Unit.name"].text,
        "measurement_unit": ts["price_Measure_Unit.name"].text,
        "start": start_time,
        "end": end_time,
        "resolution": duration,
    }

    points = []
    for elem in period.Point:
        pos = elem.position - 1
        amount = elem["price.amount"]
        begin = start_time + pos * duration

        points.append(
            {
                "start": begin,
                "end": begin + duration,
                "amount": amount,
            }
        )
    data["points"] = points

    return data


if __name__ == "__main__":
    d = day_ahead_price_list(
        """<?xml version="1.0" encoding="UTF-8"?>
    <Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0">
        <mRID>30eee84e89aa4bcfa0916411b2014eb9</mRID>
        <revisionNumber>1</revisionNumber>
        <type>A44</type>
        <sender_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</sender_MarketParticipant.mRID>
        <sender_MarketParticipant.marketRole.type>A32</sender_MarketParticipant.marketRole.type>
        <receiver_MarketParticipant.mRID codingScheme="A01">10X1001A1001A450</receiver_MarketParticipant.mRID>
        <receiver_MarketParticipant.marketRole.type>A33</receiver_MarketParticipant.marketRole.type>
        <createdDateTime>2021-10-19T10:55:41Z</createdDateTime>
        <period.timeInterval>
            <start>2021-10-18T22:00Z</start>
            <end>2021-10-19T22:00Z</end>
        </period.timeInterval>
        <TimeSeries>
            <mRID>1</mRID>
            <businessType>A62</businessType>
            <in_Domain.mRID codingScheme="A01">10YNO-3--------J</in_Domain.mRID>
            <out_Domain.mRID codingScheme="A01">10YNO-3--------J</out_Domain.mRID>
            <currency_Unit.name>EUR</currency_Unit.name>
            <price_Measure_Unit.name>MWH</price_Measure_Unit.name>
            <curveType>A01</curveType>
            <Period>
                <timeInterval>
                    <start>2021-10-18T22:00Z</start>
                    <end>2021-10-19T22:00Z</end>
                </timeInterval>
                <resolution>PT60M</resolution>
                <Point>
                    <position>1</position>
                    <price.amount>21.39</price.amount>
                </Point>
                <Point>
                    <position>2</position>
                    <price.amount>20.83</price.amount>
                </Point>
                <Point>
                    <position>3</position>
                    <price.amount>20.50</price.amount>
                </Point>
                <Point>
                    <position>4</position>
                    <price.amount>20.54</price.amount>
                </Point>
                <Point>
                    <position>5</position>
                    <price.amount>20.75</price.amount>
                </Point>
                <Point>
                    <position>6</position>
                    <price.amount>20.69</price.amount>
                </Point>
                <Point>
                    <position>7</position>
                    <price.amount>19.97</price.amount>
                </Point>
                <Point>
                    <position>8</position>
                    <price.amount>20.04</price.amount>
                </Point>
                <Point>
                    <position>9</position>
                    <price.amount>20.84</price.amount>
                </Point>
                <Point>
                    <position>10</position>
                    <price.amount>20.65</price.amount>
                </Point>
                <Point>
                    <position>11</position>
                    <price.amount>20.43</price.amount>
                </Point>
                <Point>
                    <position>12</position>
                    <price.amount>20.35</price.amount>
                </Point>
                <Point>
                    <position>13</position>
                    <price.amount>20.08</price.amount>
                </Point>
                <Point>
                    <position>14</position>
                    <price.amount>20.00</price.amount>
                </Point>
                <Point>
                    <position>15</position>
                    <price.amount>20.00</price.amount>
                </Point>
                <Point>
                    <position>16</position>
                    <price.amount>19.15</price.amount>
                </Point>
                <Point>
                    <position>17</position>
                    <price.amount>17.40</price.amount>
                </Point>
                <Point>
                    <position>18</position>
                    <price.amount>16.52</price.amount>
                </Point>
                <Point>
                    <position>19</position>
                    <price.amount>15.97</price.amount>
                </Point>
                <Point>
                    <position>20</position>
                    <price.amount>18.61</price.amount>
                </Point>
                <Point>
                    <position>21</position>
                    <price.amount>19.08</price.amount>
                </Point>
                <Point>
                    <position>22</position>
                    <price.amount>19.05</price.amount>
                </Point>
                <Point>
                    <position>23</position>
                    <price.amount>18.57</price.amount>
                </Point>
                <Point>
                    <position>24</position>
                    <price.amount>16.97</price.amount>
                </Point>
            </Period>
        </TimeSeries>
    </Publication_MarketDocument>""".encode(
            "UTF-8"
        )
    )
