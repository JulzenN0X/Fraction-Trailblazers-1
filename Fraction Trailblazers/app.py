from flask import Flask, render_template, jsonify, request
import csv
import datetime
import os
import random

app = Flask(__name__)

# OFFICIAL TEST BANK - Includes Compass hints and Examples
TRAIL_DATA = [
    {"id": 1, "part": "Part I: Conceptual Understanding", "q": "Which number line point best represents one-half?", "options": ["0.25", "0.5", "0.75", "1"], "a": "0.5", 
     "compass": "Think of the number line as a hiking trail from 0 to 1 km. If you are exactly halfway through your hike, what is your mileage? \n\nExample: On a 10-mile trail, the midpoint is mile 5. On a 1-unit trail, look for the decimal that marks that 50% mark."},
    {"id": 2, "part": "Part I: Conceptual Understanding", "q": "Which fraction is equivalent to three-fourths (3/4)?", "options": ["6/8", "3/8", "9/16", "12/20"], "a": "6/8", 
     "compass": "Equivalent fractions are like different maps of the same forest. Multiply the 'Top' and 'Bottom' by the same number! \n\nExample: If you double a 1/2 trail map, you get a 2/4 map. Try doubling the 3/4 coordinates."},
    {"id": 3, "part": "Part I: Conceptual Understanding", "q": "Arrange in ascending order: 1/2, 2/3, 3/4", "options": ["1/2, 2/3, 3/4", "1/2, 3/4, 2/3", "2/3, 1/2, 3/4", "3/4, 2/3, 1/2"], "a": "1/2, 2/3, 3/4", 
     "compass": "'Ascending' means climbing from the lowest elevation to the highest. \n\nExample: Think of fuel tanks. A 1/4 tank is lower than a 1/2 tank. Use decimals (0.5, 0.66, 0.75) to see which 'peak' is higher."},
    {"id": 4, "part": "Part I: Conceptual Understanding", "q": "Which fraction is greater?", "options": ["5/8", "3/5"], "a": "5/8", 
     "compass": "Use the 'Cross-Trail' check! Multiply the diagonals to see which path is longer. \n\nExample: To compare 1/4 and 2/6, multiply 1x6=6 and 4x2=8. Since 8 is bigger, 2/6 is greater."},
    {"id": 5, "part": "Part I: Conceptual Understanding", "q": "Which fraction equals one whole?", "options": ["7/7", "7/8", "7/6", "1/7"], "a": "7/7", 
     "compass": "You've reached the summit! A whole means you have every piece of the map. \n\nExample: If a trail is split into 10 markers and you pass all 10, you finished 10/10."},
    {"id": 6, "part": "Part II: Procedural Fluency", "q": "Add and simplify: 2/3 + 1/6", "options": ["5/6", "3/4", "1", "2/3"], "a": "5/6", 
     "compass": "You can't combine different trails unless they use the same units. \n\nExample: To add 1/5 + 2/10, change 1/5 to 2/10. Then 2/10 + 2/10 = 4/10."},
    {"id": 7, "part": "Part II: Procedural Fluency", "q": "Subtract and simplify: 5/6 - 1/2", "options": ["1/3", "2/6", "1/2", "5/12"], "a": "1/3", 
     "compass": "Make the denominators match so you are comparing the same size steps. \n\nExample: If you had 3/4 liter of water and drank 1/8, change 3/4 to 6/8."},
    {"id": 8, "part": "Part II: Procedural Fluency", "q": "Multiply and simplify: 3/4 x 2/3", "options": ["6/12", "1/2", "3/6", "5/6"], "a": "1/2", 
     "compass": "This is a direct path. Multiply the Top and Bottom. \n\nExample: 1/3 x 1/2 = (1x1)/(3x2) = 1/6."},
    {"id": 9, "part": "Part II: Procedural Fluency", "q": "Divide and simplify: 5/8 ÷ 1/4", "options": ["5/2", "1/2", "1 1/4", "2/5"], "a": "5/2", 
     "compass": "Use 'Keep, Change, Flip!' \n\nExample: 1/5 ÷ 1/2 becomes 1/5 x 2/1 = 2/5."},
    {"id": 10, "part": "Part II: Procedural Fluency", "q": "Convert to improper: 2 3/5", "options": ["13/5", "8/5", "11/5", "10/5"], "a": "13/5", 
     "compass": "Use the Circular Path. Multiply bottom by big number, add the top. \n\nExample: For 3 1/2, do 2x3=6, then 6+1=7."},
    {"id": 11, "part": "Part III: Problem-Solving Skills", "q": "A recipe needs 3/4 cup of sugar. You have a 1/2 cup measure. How many 1/2 cups do you need?", "options": ["1", "1 1/2", "2", "3/4"], "a": "1 1/2", 
     "compass": "This asks: 'How many small scoops fit into the big requirement?' Division! \n\nExample: 4 liters ÷ 1/2 liter bottles = 8 bottles."},
    {"id": 12, "part": "Part III: Problem-Solving Skills", "q": "You ran 3/8 of a 4 km track. How far did you run?", "options": ["1 km", "1 1/2 km", "2 km", "3 km"], "a": "1 1/2 km", 
     "compass": "When a trailblazer sees 'of', they think 'multiply'. \n\nExample: 1/4 of 12 miles = 12 x 1/4 = 3 miles."},
    {"id": 13, "part": "Part III: Problem-Solving Skills", "q": "A pizza is cut into 8 equal slices. You ate 3/8 and your friend ate 1/4. How much is left?", "options": ["3/8", "1/2", "5/8", "1/4"], "a": "3/8", 
     "compass": "Combine eaten territory first, then subtract from whole (8/8). \n\nExample: 2/10 + 3/10 = 5/10 eaten. 5/10 remains."},
    {"id": 14, "part": "Part III: Problem-Solving Skills", "q": "In a class, 2/5 prefer math and 1/4 prefer science. What fraction prefer either?", "options": ["3/4", "13/20", "7/10", "12"], "a": "13/20", 
     "compass": "Merging camps requires addition with a common denominator. \n\nExample: 1/2 East + 1/3 West = 5/6 total."},
    {"id": 15, "part": "Part III: Problem-Solving Skills", "q": "You need 1 1/2 meters of ribbon per gift. How much for 5 gifts?", "options": ["6 1/2 meters", "7 1/2 meters", "5 meters", "8 meters"], "a": "7 1/2 meters", 
     "compass": "Multiply length for one gift by total gifts. \n\nExample: 2.25 miles x 3 markers = 6.75 miles."}
]

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    shuffled_data = []
    for item in TRAIL_DATA:
        q_copy = item.copy()
        q_copy['options'] = random.sample(item['options'], len(item['options']))
        shuffled_data.append(q_copy)
    return jsonify(shuffled_data)

@app.route('/save_score', methods=['POST'])
def save_score():
    try:
        data = request.json
        with open('leaderboard.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data.get('name'), data.get('score'), data.get('time'), datetime.datetime.now().strftime("%Y-%m-%d")])
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/get_leaderboard')
def get_leaderboard():
    scores = []
    if os.path.exists('leaderboard.csv'):
        with open('leaderboard.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and len(row) >= 4:
                    try:
                        scores.append({"name": row[0], "score": int(row[1]), "time": int(row[2]), "date": row[3]})
                    except: continue
    return jsonify(sorted(scores, key=lambda x: (-x['score'], x['time'])))

if __name__ == '__main__':
    app.run(debug=True)