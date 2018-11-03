var surveyJSON = {
 "pages": [
  {
   "name": "page1",
   "elements": [
    {
     "type": "text",
     "name": "hourly_wage_mturk",
     "title": "How much do you earn on MTurk? (per hour)",
     "isRequired": true,
     "inputType": "number",
     "placeHolder": "30"
    },
    {
     "type": "radiogroup",
     "name": "upset_loss_mturk",
     "title": "How upset would you be if you lost the money present in your MTurk account?",
     "isRequired": true,
     "choices": [
      {
       "value": "3",
       "text": "Very"
      },
      {
       "value": "2",
       "text": "Somewhat"
      },
      {
       "value": "1",
       "text": "Slightly"
      },
      {
       "value": "0",
       "text": "Not at all"
      }
     ]
    }
   ]
  }
 ]
}
var survey = new Survey.Model(surveyJSON);
survey.completeText = "Submit";
survey.completedHtml = "Thanks!";
$("#surveyContainer").Survey({
    model:survey,
    onComplete:sendDataToServer
});
function sendDataToServer(survey) {
  var resultAsString = JSON.stringify(survey.data);
  $.ajax({
    type: 'POST',
    async: false,
    url: '/',
    data: resultAsString,
    contentType: "application/json",
    dataType: 'json'
  });
  // window.location.href = 'description.php';
}
