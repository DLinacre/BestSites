import type {Metadata} from 'next';
import Link from 'next/link';
import {ArrowLeft, Film, Smartphone, Volume2} from 'lucide-react';

export const metadata:Metadata={
  title:'GTA VI decomp recap video',
  description:'A narrated recap of the r/Piracy thread about GTA VI being decompiled to PC five days after launch, in widescreen and vertical cuts.',
  alternates:{canonical:'/video'}
};

const cuts=[
  {id:'16x9',label:'Widescreen · 16:9',file:'/video/gtavi_piracy_recap_16x9.mp4',ratio:'16 / 9',note:'YouTube-style. Best on a desktop or TV.',Icon:Film,width:1920,height:1080},
  {id:'9x16',label:'Vertical · 9:16',file:'/video/gtavi_piracy_recap_9x16.mp4',ratio:'9 / 16',note:'Shorts, Reels and TikTok. Best on a phone.',Icon:Smartphone,width:1080,height:1920}
];

const chapters=[
  'Five days after launch, and there is no PC version',
  '$4,000,000,000 in, $1.5B out: can Rockstar feel this?',
  'It is not the money, it is the security breach',
  'The union-busting theory, and the pushback',
  '"Console speaks ABC, PC speaks 123"',
  'Will it work, and will Take-Two panic-release in February?'
];

export default function VideoPage(){
  return (
    <main className="video-page page-container" id="main-content">
      <Link href="/" className="back-link"><ArrowLeft size={15}/> Back to discovery</Link>

      <header className="video-hero">
        <span className="eyebrow">WATCH · 3 MIN 25</span>
        <h1>GTA VI is already<br/><em>on PC.</em></h1>
        <p>
          A narrated recap of the r/Piracy thread about the console build being decompiled to PC five days
          after launch: the money, the security breach, the union theory and the memes.
        </p>
        <p className="video-disclaimer">
          <Volume2 size={15}/> Unofficial fan recap. Not affiliated with Rockstar or Take-Two. The $4B and
          $1.5B figures are as claimed in the thread and are unverified. Nothing here is legal advice, and
          there are no download links.
        </p>
      </header>

      <section className="video-cuts" aria-label="Video versions">
        {cuts.map(({id,label,file,ratio,note,Icon,width,height})=>(
          <article key={id} className="video-cut">
            <header className="video-cut-head">
              <span className="video-cut-icon"><Icon size={18}/></span>
              <div>
                <h2>{label}</h2>
                <p>{note}</p>
              </div>
            </header>
            <div className={`video-frame video-frame-${id}`} style={{aspectRatio:ratio}}>
              <video
                controls
                playsInline
                preload="metadata"
                width={width}
                height={height}
                aria-label={`${label} cut of the GTA VI decomp recap`}
              >
                <source src={file} type="video/mp4"/>
                Your browser cannot play this video.
                <a href={file}>Download the MP4</a> instead.
              </video>
            </div>
            <a className="video-direct" href={file}>Open the MP4 directly</a>
          </article>
        ))}
      </section>

      <section className="video-notes" aria-label="What is in the video">
        <div>
          <span className="eyebrow">IN THIS CUT</span>
          <ul className="video-chapters">
            {chapters.map((chapter,index)=>(
              <li key={chapter}><span>{String(index+1).padStart(2,'0')}</span>{chapter}</li>
            ))}
          </ul>
        </div>
        <div>
          <span className="eyebrow">HOW IT WAS MADE</span>
          <p>
            Generated narration, Reddit-style comment cards quoting the thread, a rolling revenue counter,
            a mocked decompiler window and a generated lo-fi bed. Both cuts come from the same source, so
            the scene timing follows the narration.
          </p>
          <p>
            The build script lives in the repository under <code>video/</code>. Re-run
            <code>python render.py 16x9</code> to regenerate the widescreen cut.
          </p>
          <Link className="button-secondary" href="/about">How Atlas handles sources</Link>
        </div>
      </section>
    </main>
  );
}
