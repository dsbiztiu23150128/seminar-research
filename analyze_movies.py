from pathlib import Path
import contextlib, io, json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
with contextlib.redirect_stdout(io.StringIO()):
    import audit_movie_data as audit
root=Path(__file__).resolve().parent
out=root/'data/results'; fig=root
out.mkdir(parents=True,exist_ok=True)
d=pd.DataFrame(audit.clean)
d['Year']=d.Year.astype(int)
d=d.rename(columns={'Year':'release_year'})
d['log_gross']=np.log(d.gross); d['log_budget']=np.log(d.budget); d['log_votes']=np.log(d.votes)
d['ratio']=d.gross/d.budget
d['post2006']=(d.release_year>=2007).astype(int)
base=d[d.release_year<2020].copy()
counts=base.genre.value_counts()
# Pool sparse genre categories to avoid interpreting unstable tiny samples.
d['genre_group']=d.genre.where(d.genre.isin(counts[counts>=50].index),'Other')
base=d[d.release_year<2020].copy()
formula='log_gross ~ log_budget + log_votes + score + C(genre_group) + C(release_year)'
models={
 'budget_only':smf.ols('log_gross ~ log_budget + C(genre_group) + C(release_year)',base).fit(cov_type='HC3'),
 'without_votes':smf.ols('log_gross ~ log_budget + score + C(genre_group) + C(release_year)',base).fit(cov_type='HC3'),
 'main':smf.ols(formula,base).fit(cov_type='HC3'),
 'include2020':smf.ols(formula,d).fit(cov_type='HC3'),
 'trim_ratio_top1pct':smf.ols(formula,base[base.ratio<=base.ratio.quantile(.99)]).fit(cov_type='HC3'),
 'era_interaction':smf.ols(formula+' + log_votes:post2006 + score:post2006 + log_budget:post2006',base).fit(cov_type='HC3'),
 'genre_interaction':smf.ols(formula+' + log_votes:C(genre_group)',base).fit(cov_type='HC3'),
}
rows=[]
for name,m in models.items():
    ci=m.conf_int()
    for term in m.params.index:
        rows.append(dict(model=name,term=term,coef=m.params[term],ci_low=ci.loc[term,0],ci_high=ci.loc[term,1],p=m.pvalues[term],n=int(m.nobs),r2=m.rsquared))
    (out/(name+'_regression.txt')).write_text(m.summary().as_text())
pd.DataFrame(rows).to_csv(out/'regression.csv',index=False)
low=base[base.budget<15e6]
group=low.groupby('genre').ratio.agg(['count','mean','median']).sort_values('count',ascending=False)
group.to_csv(out/'low_budget_genres.csv')
summary={'n':len(base),'genre_counts':counts.to_dict(),'models':{k:{'n':int(m.nobs),'r2':m.rsquared} for k,m in models.items()},'low_budget':{'n':len(low),'mean':low.ratio.mean(),'median':low.ratio.median(),'mean_without_top2':low.ratio.sort_values().iloc[:-2].mean(),'mean_trim_top1pct':low.loc[low.ratio<=low.ratio.quantile(.99),'ratio'].mean()},'rank':int(np.linalg.matrix_rank(models['main'].model.exog)),'parameters':models['main'].model.exog.shape[1]}
for name,prefix in [('era_interaction',':post2006'),('genre_interaction','log_votes:C(')]:
    m=models[name]; terms=[i for i,t in enumerate(m.params.index) if prefix in t]
    R=np.eye(len(m.params))[terms]
    test=m.wald_test(R,scalar=True)
    summary[name+'_joint_p']=float(test.pvalue)
(out/'analysis_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
base[['Title','IMDb code','release_year','genre','genre_group','budget','gross','votes','score','ratio']].to_csv(out/'analysis_data.csv',index=False)
plt.rcParams.update({'font.family':'Hiragino Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
f,axes=plt.subplots(1,3,figsize=(13,4.3))
for ax,col,label in zip(axes,['budget','votes','score'],['制作費（ドル・対数目盛）','投票数（Kaggle・対数目盛）','評価点（Kaggle）']):
    ax.scatter(base[col],base.gross,s=8,alpha=.18,color='#157d8d',rasterized=True)
    if col!='score': ax.set_xscale('log')
    ax.set_yscale('log'); ax.set_xlabel(label); ax.set_ylabel('興行収入（ドル・対数目盛）')
f.suptitle('映画の特徴と興行収入の関係｜1980〜2019年・3,871作品');f.tight_layout();f.savefig(fig/'01_associations.png',dpi=180);plt.close(f)
g=group[group['count']>=30].sort_values('median')
f,ax=plt.subplots(figsize=(8,5)); y=np.arange(len(g));ax.barh(y-.18,g['mean'],height=.35,label='平均',color='#157d8d');ax.barh(y+.18,g['median'],height=.35,label='中央値',color='#e6ad42');ax.set_yticks(y,[f'{a} (n={int(b)})' for a,b in zip(g.index,g['count'])]);ax.set_xlabel('興行収入 ÷ 制作費（倍）');ax.set_title('制作費1,500万ドル未満の映画：平均と中央値');ax.legend();f.tight_layout();f.savefig(fig/'02_genres.png',dpi=180);plt.close(f)
m=models['main'];terms=['log_budget','log_votes','score'];ci=m.conf_int().loc[terms]
f,ax=plt.subplots(figsize=(7,3.8)); vals=m.params[terms];ax.errorbar(vals,range(3),xerr=[vals-ci[0],ci[1]-vals],fmt='o',capsize=5,color='#157d8d');ax.axvline(0,color='gray',lw=1);ax.set_yticks(range(3),['制作費（対数）','投票数（対数）','評価点（1点）']);ax.set_xlabel('係数と95%信頼区間（HC3）');ax.set_title('条件を考慮した興行収入（対数）との関係\nジャンル・公開年を調整／横軸の単位は変数ごとに異なる');f.tight_layout();f.savefig(fig/'03_coefficients.png',dpi=180);plt.close(f)
print(json.dumps(summary,ensure_ascii=False,indent=2))
print(pd.DataFrame(rows).query("model == 'main' and term in ['log_budget','log_votes','score']").to_string(index=False))
