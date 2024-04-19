async function getQuestionData() {
    return new Promise((resolve, reject) => {
        resolve({
            "id": 12, 
            "type": "trivia", 
            "trending_topic": "testing", 
            "question": "What is Lorem Ipsum?",
            "options": [
                "Option 1", 
                "Option 2", 
                "Option 3", 
                "Option 4"
            ]
        })
    })
}

window.onload = async function(){
    const data = await getQuestionData();
    document.querySelector("#question_topic").innerHTML = data.trending_topic;
    document.querySelector("#question_type").innerHTML = data.type;
    document.querySelector("#question_question").innerHTML = data.question;
    const formElement = document.querySelector("#question_options")
    formElement.setAttribute("action", `/answer/${data.id}`)
    for (const option of data.options) {
        formElement.innerHTML += `<label><input type="radio" name="submission">${option}</label>`
    }
    // Submit on click any option
    formElement.addEventListener('change', formElement.submit);
}

