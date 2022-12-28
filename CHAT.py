import os
import openai

# openai.api_key = os.getenv("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")
openai.api_key = "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"

response = openai.Completion.create(
  model="text-davinci-003",
  prompt=" 抽取语句谁在说话\n\n说着，引人步入茆堂，里面纸窗木榻，富贵气象一洗皆尽．贾政心中自是欢喜，却瞅宝玉道。\n\n",
  temperature=0.7,
  max_tokens=3000,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
response = response.get('choices')[0].get('text')
tt = response.encode('gb2312')
tt = tt.decode('gb2312')
print(tt)