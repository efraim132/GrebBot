import {Button, Box, Heading, Stack} from '@primer/react'
import {MarkGithubIcon} from '@primer/octicons-react'
import MyActionMenu from './myActionMenu'
import './App.css'

export default function App() {
  return ( 
  <>
    
      <Heading class="mb-2" as="h2">
        <MarkGithubIcon size={64} /> Primer + Vite + TS
      </Heading>
      <Stack direction="vertical">
        <Button onClick={() => alert('Hello, Primer!')}>Click me</Button>
        <MyActionMenu />
      </Stack>
      
    
      
    </>
  )
}
