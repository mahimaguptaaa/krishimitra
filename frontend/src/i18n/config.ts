import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import en from './locales/en/translation.json'
import hi from './locales/hi/translation.json'
import pa from './locales/pa/translation.json'
import mr from './locales/mr/translation.json'
import bn from './locales/bn/translation.json'
import ta from './locales/ta/translation.json'
import te from './locales/te/translation.json'
import gu from './locales/gu/translation.json'
import kn from './locales/kn/translation.json'
import ml from './locales/ml/translation.json'

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en }, hi: { translation: hi }, pa: { translation: pa },
    mr: { translation: mr }, bn: { translation: bn }, ta: { translation: ta },
    te: { translation: te }, gu: { translation: gu }, kn: { translation: kn },
    ml: { translation: ml },
  },
  lng: typeof window !== 'undefined' ? (localStorage.getItem('km_lang') || 'hi') : 'hi',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
