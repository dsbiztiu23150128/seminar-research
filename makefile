.PHONY: preview render clean preview-slides render-slides render-all cache-refresh git publish

preview:
	quarto preview &

render:
	quarto render
	$(MAKE) render-slides

preview-slides:
	quarto preview a1_発表資料.qmd &

render-slides:
	quarto render a1_発表資料.qmd
	npx decktape reveal a1_発表資料.html a1_発表資料.pdf --size 1280x720 --chrome-arg=--no-sandbox
	quarto render a1_発表資料.qmd --to pptx --cache-refresh
	cp a1_発表資料.html docs/
	cp a1_発表資料.pdf docs/
	cp a1_発表資料.pptx docs/
	cp -r a1_発表資料_files docs/ 2>/dev/null || true
	rm -f a1_発表資料.html a1_発表資料.pdf a1_発表資料.pptx
	rm -rf a1_発表資料_files

render-all: render

cache-refresh:
	rm -rf a1_発表資料_cache
	quarto render a1_発表資料.qmd --cache-refresh

git:
	git add -A
	git commit -m "Update"
	git push

publish: git
	quarto publish gh-pages --no-prompt

clean:
	rm -rf docs .quarto a1_発表資料.html a1_発表資料.pdf a1_発表資料.pptx a1_発表資料_files a1_発表資料_cache
