/* Local navigation only: no generation, network requests, or input storage. */
(() => {
 'use strict';
 if (!document.body.classList.contains('studio-editorial') || document.body.classList.contains('studio-login') || document.body.dataset.focusedUx) return;
 document.body.dataset.focusedUx='true';
 const normalize=value=>String(value).normalize('NFKC').toLocaleLowerCase().trim();
 const matches=(text,query)=>normalize(query).split(/\s+/).every(word=>normalize(text).includes(word));
 const make=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text)el.textContent=text;return el;};

 // Keep every course in the HTML; show a smaller choice only after enhancement.
 const courseList=document.querySelector('#course-voices');
 if(courseList){
  const cards=[...courseList.querySelectorAll('.compact-course-card')];
  if(cards.length===6){
   const groups=[['all','すべて'],['learn','学ぶ・試す'],['team','組織で使う'],['build','制作を任せる']];
   const bar=make('div','ux-filters');bar.setAttribute('role','group');bar.setAttribute('aria-label','コースを目的で絞る');
   const status=make('p','ux-result-status');status.setAttribute('role','status');
   const categories=['learn','learn','learn','team','learn','build'];
   groups.forEach(([id,label])=>{const button=make('button','',label);button.type='button';button.setAttribute('aria-pressed',String(id==='all'));
    button.addEventListener('click',()=>{bar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));cards.forEach((card,i)=>{card.hidden=id!=='all'&&categories[i]!==id;});status.textContent=`${label}：${cards.filter(c=>!c.hidden).length}件`;});bar.append(button);
   });
   courseList.before(bar);courseList.after(status);
   // Direct links must never land on a filtered-out course.
   window.addEventListener('hashchange',()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(id);const card=target?.closest('.compact-course-card');if(card?.hidden){bar.querySelector('button').click();target.scrollIntoView({block:'start'});}});
  }
 }
 const adminHub=document.querySelector('[data-ux-admin-hub]');
 if(adminHub && /^\/admin\/?$/.test(location.pathname)){adminHub.hidden=false;const original=document.querySelector('body > .container');if(original){original.hidden=true;original.classList.add('ux-original-admin');}}
 const taskBrowser=document.querySelector('.ux-task-browser');
 if(taskBrowser){
  const controls=taskBrowser.querySelector('.ux-task-controls'),search=taskBrowser.querySelector('input'),cards=[...taskBrowser.querySelectorAll('.ux-task-card')],buttons=[...taskBrowser.querySelectorAll('[data-ux-filter]')];
  let category='all';
  const render=()=>{cards.forEach(card=>{card.hidden=!(category==='all'||card.dataset.uxCategory===category)||!matches(card.textContent+' '+card.dataset.uxKeywords,search.value);});const count=cards.filter(c=>!c.hidden).length;taskBrowser.querySelector('.ux-empty').hidden=count!==0;taskBrowser.querySelector('.ux-result-status').textContent=`${count}件の作業`;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.uxFilter===category)));};
  buttons.forEach(button=>button.addEventListener('click',()=>{category=button.dataset.uxFilter;if(category==='all')search.value='';render();}));
  search.addEventListener('input',()=>{category='all';render();});controls.hidden=false;render();
 }

 const header=document.querySelector('.site-header-inner');
 if(!header || typeof HTMLDialogElement==='undefined')return;
 const admin=document.body.classList.contains('studio-admin')||document.body.classList.contains('admin-page');
 let commands;
 if(admin){
  const unique=new Map();
  document.querySelectorAll('.admin-shared-header a[href],.ux-task-card').forEach(a=>{const href=a.getAttribute('href');if(!href?.startsWith('/')||href.startsWith('//')||href.includes('logout'))return;if(!unique.has(href))unique.set(href,{href,label:(a.querySelector('strong,h3')?.textContent||a.textContent).trim().replace(/\s+/g,' ')});});
  commands=[...unique.values()];
 }else commands=[{label:'講習・相談コース',href:'/#packages'},{label:'AI実力診断',href:'/ai-agent-readiness/'},{label:'サイト診断',href:'/seo-llmo-diagnosis/'},{label:'AIニュース・Codex',href:'/ai-news/'},{label:'AIアプリサイト制作',href:'/ai-app-site/'},{label:'受講資料',href:'/lectures/index.html'},{label:'ブログ',href:'/blog/'},{label:'講師紹介',href:'/speaker.html'},{label:'実績サイト',href:'/#all-works'},{label:'困っている仕事を相談する',href:'/#contact'}];
 if(!commands.length)return;
 const launch=make('button','ux-launcher','探す');launch.type='button';launch.setAttribute('aria-haspopup','dialog');launch.setAttribute('aria-label',admin?'管理作業を探す':'目的のページを探す');
 const dialog=make('dialog','ux-command-dialog');dialog.setAttribute('aria-labelledby','ux-command-title');
 const top=make('div','ux-command-top');const title=make('h2','',admin?'どの作業へ進みますか？':'どこから始めますか？');title.id='ux-command-title';const close=make('button','ux-command-close','閉じる');close.type='button';top.append(title,close);
 const label=make('label','ux-search-label','キーワードで探す');const input=make('input');input.type='search';input.placeholder=admin?'記事、SNS、予定…':'講習、診断、資料…';input.autocomplete='off';label.append(input);
 const list=make('div','ux-command-results');const empty=make('p','ux-empty','見つかりませんでした。別の言葉で探してください。');empty.hidden=true;
 const count=make('p','ux-result-status');count.setAttribute('role','status');
 const links=commands.map(item=>{const a=make('a','',item.label);a.href=item.href;a.addEventListener('click',()=>dialog.close());list.append(a);return a;});
 dialog.append(top,label,list,empty,count);document.body.append(dialog);header.append(launch);
 let previous;
 const filter=()=>{links.forEach(a=>a.hidden=!matches(a.textContent,input.value));const visible=links.filter(a=>!a.hidden).length;empty.hidden=visible!==0;count.textContent=`${visible}件`;};
 const open=()=>{if(dialog.open||document.querySelector('dialog[open]'))return;previous=document.activeElement;input.value='';filter();dialog.showModal();input.focus();};
 launch.addEventListener('click',open);close.addEventListener('click',()=>dialog.close());input.addEventListener('input',filter);
 input.addEventListener('keydown',event=>{if(event.key==='ArrowDown'){event.preventDefault();links.find(a=>!a.hidden)?.focus();}});
 dialog.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();dialog.close();}});
 dialog.addEventListener('close',()=>{if(previous?.isConnected)previous.focus();});
 document.addEventListener('keydown',event=>{if((event.ctrlKey||event.metaKey)&&!event.altKey&&event.key.toLowerCase()==='k'&&!document.querySelector('dialog[open]')){event.preventDefault();open();}});
})();
