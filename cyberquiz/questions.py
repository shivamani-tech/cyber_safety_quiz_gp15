"""Question bank and scoring rules."""
QUESTIONS = [
    {"id":"P1","category":"Password Safety","prompt":"Which password is strongest?","options":["password123","Shivamani@123","T7!qL9#vP2$x","12345678"],"answer":2,"explanation":"A long, unique password with mixed character types is harder to guess."},
    {"id":"F1","category":"Phishing","prompt":"An email asks you to verify your bank account through an unfamiliar link. What should you do?","options":["Click immediately","Reply with your password","Avoid the link and contact the bank using its official channel","Forward it to friends"],"answer":2,"explanation":"Unexpected links requesting sensitive details are a common phishing warning sign."},
    {"id":"O1","category":"Online Safety","prompt":"What should you do before installing an app?","options":["Check its source, permissions and reviews","Allow every permission","Download from any pop-up","Share your OTP"],"answer":0,"explanation":"Use trusted sources and review permissions before installing."},
    {"id":"P2","category":"Password Safety","prompt":"Why avoid reusing the same password on multiple sites?","options":["It slows the internet","One breached account could expose other accounts","It changes your username","There is no reason"],"answer":1,"explanation":"A breach on one service can put every account using that password at risk."},
    {"id":"F2","category":"Phishing","prompt":"A message says you won a prize but asks you to pay a fee first. This is most likely:","options":["A guaranteed reward","A phishing or scam attempt","A system update","A secure login"],"answer":1,"explanation":"Unexpected prizes with upfront payment requests are a strong scam warning."},
    {"id":"O2","category":"Online Safety","prompt":"What is the safest way to use public Wi-Fi?","options":["Do banking on any open network","Turn off device security","Avoid sensitive activity or use a trusted VPN","Share files with everyone"],"answer":2,"explanation":"Open networks can expose traffic; avoid sensitive activity unless protected."},
    {"id":"P3","category":"Password Safety","prompt":"What is two-factor authentication (2FA)?","options":["Using two usernames","An extra verification step beyond your password","Sharing your password twice","Changing screen brightness"],"answer":1,"explanation":"2FA adds a second proof of identity, such as an authenticator code."},
    {"id":"O3","category":"Online Safety","prompt":"Someone online asks for your OTP. What should you do?","options":["Share it if they sound official","Post it in a group","Never share it; report suspicious requests","Send a screenshot"],"answer":2,"explanation":"Never disclose your OTP, even to someone claiming to be support."}
]

def grade(answers):
    if len(answers) != len(QUESTIONS):
        raise ValueError("Answer count does not match question bank.")
    score = sum(answer == question["answer"] for answer, question in zip(answers, QUESTIONS))
    categories = {}
    review = []
    for answer, question in zip(answers, QUESTIONS):
        category = question["category"]
        item = categories.setdefault(category, {"score": 0, "total": 0})
        item["total"] += 1
        correct = answer == question["answer"]
        item["score"] += int(correct)
        review.append({
            "question_id": question["id"], "correct": correct,
            "correct_answer": question["options"][question["answer"]],
            "explanation": question["explanation"]
        })
    return {"score": score, "total": len(QUESTIONS),
            "percentage": round(score / len(QUESTIONS) * 100),
            "passed": score / len(QUESTIONS) >= 0.70,
            "category_scores": categories, "review": review}
