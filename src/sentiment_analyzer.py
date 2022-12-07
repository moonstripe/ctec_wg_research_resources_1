from tokenize import Double
import torch
from transformers import AutoModelForSequenceClassification
from transformers import BertTokenizerFast


class DoubleRubertAnalyzer:
    def __init__(self):
        # trained on only microblogging data (2018)
        self.s = {
            "tokenizer": BertTokenizerFast.from_pretrained('blanchefort/rubert-base-cased-sentiment-rusentiment'),
            "model": AutoModelForSequenceClassification.from_pretrained('blanchefort/rubert-base-cased-sentiment-rusentiment', return_dict=True)
        }
        # trained on multiple microblogging data sets (2012, 2018), and two review sources
        self.r = {
            "tokenizer": BertTokenizerFast.from_pretrained('blanchefort/rubert-base-cased-sentiment'),
            "model": AutoModelForSequenceClassification.from_pretrained('blanchefort/rubert-base-cased-sentiment', return_dict=True)
        }

    def __str__(self):
        return f"This model uses (s for social) rubert cased rusentiment and (r for reviews) rubert cased sentiment"

    def set_text(self, text):
        self.text = text
        # print("text set to:\n", self.text)

        return

    def set_arr(self, arr):
        self.arr = arr

    """
        @params: text
        This function predicts sentiment using the only the social data
        huggingface repo: blanchefort/rubert-base-cased-sentiment
    """
    @torch.no_grad()
    def s_predict(self):
        if (len(self.text) < 1):
            print('you have not passed a string')
            return ((-1, -1, -1), -1)

        inputs = self.s['tokenizer'](self.text, max_length=512, padding=True, truncation=True, return_tensors='pt')
        outputs = self.s['model'](**inputs)
        sm_predicted = torch.nn.functional.softmax(outputs.logits, dim=1)
        am_predicted = torch.argmax(sm_predicted, dim=1).numpy()
        return ((round(sm_predicted[0][0].item(), 2), round(sm_predicted[0][1].item(), 2), round(sm_predicted[0][2].item(),2)), int(am_predicted[0]))

    """
        @params: text
        This function predicts sentiment using mulitple review sources, and multiple social repositories
        huggingface repo: blanchefort/rubert-base-cased-sentiment
    """

    @torch.no_grad()
    def r_predict(self):
        if (len(self.text) < 1):
            print('you have not passed a string')
            return ((-1, -1, -1), -1)


        inputs = self.r['tokenizer'](self.text, max_length=512, padding=True, truncation=True, return_tensors='pt')
        outputs = self.r['model'](**inputs)
        sm_predicted = torch.nn.functional.softmax(outputs.logits, dim=1)
        am_predicted = torch.argmax(sm_predicted, dim=1).numpy()
        return ((round(sm_predicted[0][0].item(), 2), round(sm_predicted[0][1].item(), 2), round(sm_predicted[0][2].item(),2)), int(am_predicted[0]))

    def run(self):
        if len(self.arr) < 1:
            print('must pass an arr')

        ret_arr = []

        for i in self.arr:
            self.set_text(i['text'])
            tup = self.r_predict()
            ret_arr.append(tup)

        return ret_arr


    def test(self):
        # print('s_predict:\t', self.s_predict())
        print('r_predict:\t', self.r_predict())



if __name__ == "__main__":
    rubert = DoubleRubertAnalyzer()
    rubert.set_text("знаю, ты сможешь во всём разобраться. я в тебя верю")
    rubert.test()
