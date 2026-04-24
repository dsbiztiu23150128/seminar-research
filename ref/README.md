# ref/ ディレクトリ

参考文献の BibTeX ファイルを格納するディレクトリです。

## 使い方

### 1. `references.bib` に文献を追加する

BibTeX 形式で文献情報を記述します。以下は代表的なエントリの例です。

**論文（article）：**
```bibtex
@article{Tanaka2024,
  author  = {田中 太郎 and 鈴木 花子},
  title   = {機械学習を用いた需要予測に関する研究},
  journal = {情報処理学会論文誌},
  volume  = {65},
  number  = {3},
  pages   = {101--115},
  year    = {2024},
  doi     = {10.xxxx/xxxxx}
}
```

**書籍（book）：**
```bibtex
@book{Yamada2023,
  author    = {山田 一郎},
  title     = {データサイエンス入門},
  publisher = {出版社名},
  year      = {2023}
}
```

**学会発表（inproceedings）：**
```bibtex
@inproceedings{Sato2025,
  author    = {佐藤 次郎},
  title     = {深層学習による時系列予測},
  booktitle = {第○回人工知能学会全国大会},
  year      = {2025},
  pages     = {1--4}
}
```

### 2. 本文から引用する

Quarto の `.qmd` ファイル内で `@引用キー` と記述すると、自動的に参考文献として表示されます。

```markdown
先行研究 [@Tanaka2024] では、機械学習を用いた需要予測が検討されている。

複数文献の同時引用も可能 [@Tanaka2024; @Yamada2023]。
```

### 3. BibTeX エントリの取得方法

- **Google Scholar**: 論文を検索 → 引用マーク（❞）→ BibTeX をクリック
- **DOI から取得**: `https://doi.org/DOIコード` にアクセス → BibTeX 形式でエクスポート
- **CiNii Research**: 論文ページ → エクスポート → BibTeX

## 注意事項

- 引用キー（例：`Tanaka2024`）は `references.bib` 内で一意にしてください
- `_quarto.yml` の `bibliography: ref/references.bib` で自動的に読み込まれます
- 本文中で引用されていない文献は参考文献リストに表示されません
