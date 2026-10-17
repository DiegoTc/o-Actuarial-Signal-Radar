'use client';
import {useEffect,useState} from 'react';
/** Presentation-only layout hint for readable month labels on phones. */
export function useNarrowChart(){
 const [narrow,setNarrow]=useState(false);
 useEffect(()=>{const media=window.matchMedia('(max-width: 760px)');const update=()=>setNarrow(media.matches);update();media.addEventListener('change',update);return()=>media.removeEventListener('change',update);},[]);
 return narrow;
}
