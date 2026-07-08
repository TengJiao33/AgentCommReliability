# Papers Cache

这个目录保存本项目近期阅读的论文原文 PDF，以及可复用的文本抽取结果。

## 当前缓存

文本缓存目录：

```text
papers/text/
```

关键文件：

```text
papers/text/manifest.json
papers/text/*.txt
papers/text/*.pages.json
scripts/extract_paper_texts.py
```

`manifest.json` 记录每个 PDF 的源文件名、页数、字符数、文件大小、修改时间、哈希值，以及本次是否复用了缓存。每篇 `.txt` 文件开头也记录了源 PDF、抽取时间、页数和标题；每篇 `.pages.json` 记录逐页字符数，方便之后定位坏页或低质量抽取页。

## 复用方式

默认运行会跳过已经抽取过的 PDF，只刷新总清单：

```powershell
python scripts/extract_paper_texts.py
```

只有确实需要重转文字时才使用：

```powershell
python scripts/extract_paper_texts.py --force
```

这样后续继续读论文时，可以直接读 `papers/text/*.txt`，不必重复转 PDF。
