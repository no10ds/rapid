import { ReactElement, ReactNode } from 'react'

type Props = {
  condition: boolean
  wrapper: (children: ReactNode) => ReactElement
  children: ReactElement
}

const ConditionalWrapper = ({ condition, wrapper, children }: Props) =>
  condition ? wrapper(children) : children

export default ConditionalWrapper
