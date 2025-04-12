from flask import Flask

app = Flask(__name__)

@app.route('/test_technical_analysis')
def test_analysis():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Technical Analysis Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            ul { margin-top: 20px; }
            li { margin-bottom: 10px; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Test Technical Analysis Page</h1>
        <p>This is a simple test to check if technical analysis pages are working</p>
        
        <h2>Click the links below to test technical analysis routing:</h2>
        <ul>
            <li><a href="/technical_analysis/BTC-USDT">Test BTC-USDT</a></li>
            <li><a href="/technical_analysis/ETH-USDT">Test ETH-USDT</a></li>
            <li><a href="/technical_analysis/SOL-USDT">Test SOL-USDT</a></li>
        </ul>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)